import os
import re
import time
import shutil
import logging

import boto

from easyaws.libs import interface, aws, ssh


logger = logging.getLogger(__name__)


class FindDjangoProject():
    __ignore_patterns = (
        # Bytecode
        '__pycache__', '.pyc',

        # Git
        '.git', '.gitignore',

        # Svn
        '.svn',

        # Cvs
        'CVS',

        # PyCharm
        '.idea',
    )

    def __init__(self):
        """
        Find django project in the current directory
        """

        self.project_path = os.getcwd()
        self.manage_path = os.path.join(self.project_path, 'manage.py')
        self.system_requirements_path = os.path.join(self.project_path, 'system-requirements.txt')

        logger.debug('Try to find django project on the path: {}'.format(self.project_path))

        # Check manage.py
        if not os.path.isfile(self.manage_path):
            interface.exit_error('File manage.py is not found')
        self.project_path = os.getcwd()
        logger.debug('File manage.py is found')

        # Find name of the django project
        with open(self.manage_path, 'r') as manage:
            pattern = r'"(\w+)\.settings"'
            result = re.search(pattern, manage.read())
            if not result:
                interface.exit_error('Name of the django project is not found in manage.py')
        self.project_name = result.group(1)
        logger.debug('Name of the project is "{}"'.format(self.project_name))

        # Check wsgi.py
        self.wsgi_path = os.path.join(self.project_path, self.project_name, 'wsgi.py')
        if not os.path.isfile(self.wsgi_path):
            interface.exit_error('File wsgi.py is not found in the project directory')
        logger.debug('File manage.py is found')

        # Find system requirements
        self.system_requirements = []
        if os.path.isfile(self.system_requirements_path):
            self.system_requirements += open(self.system_requirements_path).read().split()
            logger.debug('System requirements: {}'.format(', '.join(self.system_requirements)))

        # Generate id of the project contains letter or digits only for using in aws
        self.aws_name = ''.join([i for i in self.project_name if i.isalnum()])
        logger.debug('AWS name of the project is "{}"'.format(self.aws_name))

    def create_archive(self, archive_format='gztar'):
        """
        Archive cleaned django project (without git, bytocide etc)

        :type archive_format: str
        :param archive_format: format of archive

        :return: path to archive
        """

        # Check archive format
        if archive_format not in [a[0] for a in shutil.get_archive_formats()]:
            interface.exit_error('Unsupported archive format: {}'.format(archive_format))

        # Copy project to temp directory
        logger.debug('Copy django project to temporary directory')
        temp_path = '/tmp/{}'.format(self.project_name)
        shutil.rmtree(temp_path, ignore_errors=True)
        shutil.copytree(self.project_path, temp_path, ignore=shutil.ignore_patterns(*self.__ignore_patterns))

        # Make archive
        logger.debug('Archive django project')
        path = shutil.make_archive('/tmp/{}'.format(self.project_name), archive_format, temp_path)

        # Return archive path
        return path


class Commands:
    @classmethod
    def configure(cls):
        """
        Configure boto, i.e enter AWS credentials and select region
        """

        # Request credentials
        aws_access_key_id = interface.request(
            'Enter AWS_ACCESS_KEY_ID',
            boto.config.get('Credentials', 'aws_access_key_id'))
        aws_secret_access_key = interface.request(
            'Enter AWS_SECRET_ACCESS_KEY',
            boto.config.get('Credentials', 'aws_secret_access_key'))

        # Request region
        aws_region_name = interface.select('Select region', aws.get_regions())

        # Save them to file
        config_path = os.path.join(os.path.expanduser('~'), '.boto')
        with open(config_path, 'w') as f:
            content = str(
                '[Credentials]\n'
                'aws_access_key_id = {aws_access_key_id}\n'
                'aws_secret_access_key = {aws_secret_access_key}\n'
                '\n'
                '[Boto]\n'
                'aws_region_name = {aws_region_name}'  # for libs.aws module
            ).format(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_region_name=aws_region_name
            )
            f.write(content)

        # Hide config file
        os.chmod(config_path, 0o600)

    @classmethod
    def status(cls):
        """
        Show statuses of AWS-services in current region
        """

        # Auto scaling groups
        auto_scaling_groups = aws.connections.autoscale.get_all_groups()
        if auto_scaling_groups:
            print('Auto scaling groups:')
        for group in auto_scaling_groups:
            print(' - {} (min size: {}, max size: {}, launch configuration: {}, load_balancers: {})'.format(
                group.name,
                group.min_size,
                group.max_size,
                group.launch_config_name,
                ', '.join(group.load_balancers)
            ))

        # Launch configurations
        launch_configurations = aws.connections.autoscale.get_all_launch_configurations()
        if launch_configurations:
            print('Launch configurations:')
        for configuration in launch_configurations:
            print(' - {} (image: {}, instance type: {})'.format(
                configuration.name,
                configuration.image_id,
                configuration.instance_type))

        # Load balancers
        load_balancers = aws.connections.elb.get_all_load_balancers()
        if load_balancers:
            print('Load balancers:')
        for balancer in load_balancers:
            print(' - {balancer.name} ({balancer.dns_name})'.format(balancer=balancer))

        # Images
        images = aws.helpers.get_all_images()
        if images:
            print('Images:')
        for image in images:
            print(' - {}'.format(image.name))

        # Instances
        instances = aws.helpers.get_all_instances()
        if instances:
            print('Instances:')
        for instance in instances:
            print(' - {instance.id} ({instance.public_dns_name})'.format(instance=instance))
            for key, value in instance.tags.items():
                print('   {}: {}'.format(key, value))

        # Key pairs
        key_pairs = aws.connections.ec2.get_all_key_pairs()
        if key_pairs:
            print('Key pairs:')
        for key in key_pairs:
            print(' - {}'.format(key.name))

        # Security groups
        security_groups = aws.connections.ec2.get_all_security_groups()
        if security_groups:
            print('Security groups:')
        for group in security_groups:
            print(' - {}'.format(group.name))
            for rule in group.rules:
                print('   {} from {} to {} for {}'.format(
                    'all traffic' if rule.ip_protocol == '-1' else rule.ip_protocol,
                    rule.from_port or '0-65535',
                    rule.to_port or '0-65535',
                    ', '.join([str(grant) for grant in rule.grants])))

    @classmethod
    def clean(cls):
        """
        Full clean AWS cloud, i.e remove all auto scaling groups, launch configurations, load balancers, images,
        instances, key pairs and security groups
        """

        # Request confirmation
        if not interface.confirm():
            return

        # Remove all auto scaling groups
        for group in aws.connections.autoscale.get_all_groups():
            aws.helpers.delete_auto_scaling_group(group.name)

        # Remove all launch configurations
        for configuration in aws.connections.autoscale.get_all_launch_configurations():
            aws.helpers.delete_launch_configuration(configuration.name)

        # Remove all load balancers
        for balancer in aws.connections.elb.get_all_load_balancers():
            aws.helpers.delete_load_balancer(balancer.name)

        # Remove all images
        for image in aws.helpers.get_all_images():
            aws.helpers.delete_image(image)

        # Remove all instances
        for instance in aws.helpers.get_all_instances():
            aws.helpers.delete_instance(instance)

        # Remove all key pairs
        for key in aws.connections.ec2.get_all_key_pairs():
            aws.helpers.delete_key_pair(key.name)

        # Remove all security groups
        for security_group in aws.connections.ec2.get_all_security_groups():
            if security_group.name == 'default':
                continue
            aws.helpers.delete_security_group(security_group.name)

    class Project:
        """
        Django project deployment
        """

        @classmethod
        def push(cls):
            """
            Create and setup temporary instance, upload your django project on instance, create image and remove
            instance
            """

            # Find django project
            django_project = FindDjangoProject()

            # Create security group
            security_group = aws.helpers.get_or_create_security_group('develop', [22, 80])

            # Create key pair
            key_pair = aws.helpers.get_or_create_key_pair('develop')

            # Create unnamed instance
            instance = aws.helpers.create_instance(key_pair.name, security_group.name)

            # Prepare
            replacements = {
                'PROJECT_NAME': django_project.project_name,
                'PROJECT_PATH': '/home/ubuntu/{}'.format(django_project.project_name),
                'VIRTUALENV_PATH': '/home/ubuntu/virtualenv',
            }
            packages = ['python-pip']
            files = [
                (django_project.create_archive(), '/tmp/project.tar.gz'),
                ('templates/nginx.conf', '/tmp/nginx.conf'),
                ('templates/nginx-app-proxy', '/tmp/nginx-app-proxy'),
                ('templates/gunicorn.conf.py', '/tmp/gunicorn.conf.py'),
                ('templates/supervisord.conf', '/tmp/my.supervisord.conf'),
                ('templates/supervisord-init', '/tmp/supervisord-init'),
            ]
            receipt = [
                # Create virtualenv
                'sudo pip install virtualenv',
                'virtualenv -p /usr/bin/python3 /home/ubuntu/virtualenv',

                # Extract django-project
                'mkdir {PROJECT_PATH}',
                'tar -xvzf /tmp/project.tar.gz -C {PROJECT_PATH}',

                # Install pip requirements
                '[ -f {PROJECT_PATH}/requirements.txt ]'
                ' && source /home/ubuntu/virtualenv/bin/activate'
                ' && pip install -r {PROJECT_PATH}/requirements.txt'
                ' || echo skip',

                # Install django in the virtualenv
                'source /home/ubuntu/virtualenv/bin/activate'
                ' && pip install django',

                # Install proxy-server Nginx and configure it
                'sudo apt-get install nginx -y',
                'sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.old',
                'sudo mv /tmp/nginx.conf /etc/nginx/nginx.conf',
                'sudo chown root:root /etc/nginx/nginx.conf',
                'sudo rm -rf /etc/nginx/sites-enabled/default',
                'sudo mv /tmp/nginx-app-proxy /etc/nginx/sites-available/{PROJECT_NAME}',
                'sudo ln -sf /etc/nginx/sites-available/{PROJECT_NAME} /etc/nginx/sites-enabled/{PROJECT_NAME}',
                'sudo chown root:root /etc/nginx/sites-available/{PROJECT_NAME}',
                'sudo /etc/init.d/nginx restart',

                # Install Gunicorn in the virtualenv and configure it
                'source /home/ubuntu/virtualenv/bin/activate'
                ' && pip install gunicorn',
                'mv /tmp/gunicorn.conf.py {PROJECT_PATH}/gunicorn.conf.py',

                # Install Supervisor and configure it
                'sudo pip install supervisor',
                'echo_supervisord_conf > /tmp/supervisord.conf',
                'cat /tmp/my.supervisord.conf >> /tmp/supervisord.conf',
                'sudo mv /tmp/supervisord.conf /etc/supervisord.conf',
                'sudo supervisord',
                'sudo mv /tmp/supervisord-init /etc/init.d/supervisord',
                'sudo chmod +x /etc/init.d/supervisord',
                'sudo update-rc.d supervisord defaults',
            ]

            try:
                # Connect to the instance
                key_path = aws.helpers.generate_path_to_key_pair(key_pair.name)
                client = ssh.Client(instance.public_dns_name, key_path=key_path, replacements=replacements)

                # Setup instance
                client.put_files(files)
                client.apt_install(set(packages + django_project.system_requirements))
                client.run_commands(receipt)

            except ssh.ClientError as e:
                interface.exit_error(e.message)

            else:
                # Check availability of the instance
                aws.helpers.wait_host(instance.public_dns_name)

                # Create image based on the instance
                image_name = '{project_name}-{timestamp}'.format(
                    project_name=django_project.aws_name,
                    timestamp=time.strftime('%Y.%m.%d-%H.%M'))
                aws.helpers.create_image(image_name, instance)

                interface.exit_success('Image "{}" is created'.format(image_name))

            finally:
                # Remove instance
                aws.helpers.delete_instance(instance, wait=False)

        @classmethod
        def deploy(cls):
            """
            Create load balancer, create launch configuration based on the created image and create auto scaling group
            (auto scaling up to 3 instances when CPU-load > 70)
            """

            # Find django project
            django_project = FindDjangoProject()

            # Select image
            images = aws.helpers.get_all_images(filters={'name': django_project.aws_name + '*'}, reverse=True)
            image = interface.select('Please select image', images, title=lambda img: img.name or img.id)
            if not image:
                interface.exit_error('There are no images in the your cloud')

            # Create key
            key_pair = aws.helpers.get_or_create_key_pair(django_project.aws_name)

            # Create security group
            security_group = aws.helpers.get_or_create_security_group(django_project.aws_name)

            # Create new load balancer or get already created
            load_balancer = aws.helpers.create_load_balancer(
                django_project.aws_name,
                security_group.name,
                listeners=[(80, 80, 'http'), (443, 443, 'tcp')],
            )

            # Remove previous auto scaling group
            aws.helpers.delete_auto_scaling_group(django_project.aws_name)

            # Remove previous launch configuration
            aws.helpers.delete_launch_configuration(django_project.aws_name)

            # Create launch configuration
            launch_configuration = aws.helpers.create_launch_configuration(
                django_project.aws_name,
                image.id,
                key_pair.name,
                security_group.name,
            )

            # Create auto scaling group
            aws.helpers.create_auto_scaling_group(
                django_project.aws_name,
                load_balancer.name,
                launch_configuration.name,
            )

            # Check availability of the load balancer
            aws.helpers.wait_host(load_balancer.dns_name)

            interface.exit_success('Now to access to the project you can add CNAME:\n' + load_balancer.dns_name)

        @classmethod
        def undeploy(cls):
            """
            Remove auto scaling group and launch configuration
            """

            # Find django project
            django_project = FindDjangoProject()

            # Remove auto scaling group
            aws.helpers.delete_auto_scaling_group(django_project.aws_name)

            # Remove launch configuration
            aws.helpers.delete_launch_configuration(django_project.aws_name)

        @classmethod
        def remint(cls):
            """
            Setup EC2-instance with Python interpreter for remote environment
            """

            # Find django project
            django_project = FindDjangoProject()
            key = aws.helpers.get_or_create_key_pair(django_project.aws_name)

            # Find or create instance
            name = '{}-remote-interpreter'.format(django_project.aws_name)
            security_group = aws.helpers.get_or_create_security_group(name, [22])
            instance = aws.helpers.get_instance(name) or aws.helpers.create_instance(
                key.name,
                security_group.name,
                name=name)

            # Connect to the instance via SSH
            key_path = aws.helpers.generate_path_to_key_pair(key.name)
            client = ssh.Client(instance.public_dns_name, key_path=key_path)

            # Setup the instance
            if django_project.system_requirements:
                client.apt_install(django_project.system_requirements)

            interface.exit_success('Now you can connect to instance ubuntu@{} by key {}'.format(
                instance.public_dns_name,
                key_path))

    class Vpn:
        """
        Create or terminate VPN-server
        """

        @classmethod
        def create(cls):
            """
            Create EC2-instance with VPN-server
            """

            # Request credentials
            username = interface.request('Specify username', 'john')
            password = interface.request('Specify password', 'smith')

            # Create or get instance
            key = aws.helpers.get_or_create_key_pair('vpn')
            security_group = aws.helpers.get_or_create_security_group('vpn', [22, 1723])
            instance = aws.helpers.get_instance('vpn') or aws.helpers.create_instance(
                key.name,
                security_group.name,
                name='vpn'
            )

            # Connect to the instance via SSH
            key_path = aws.helpers.generate_path_to_key_pair(key.name)
            client = ssh.Client(instance.public_dns_name, key_path=key_path)

            # Setup the instance
            # from https://www.digitalocean.com/community/tutorials/how-to-setup-your-own-vpn-with-pptp
            client.apt_install(['pptpd'])
            client.run_commands([
                # Setup addresses of virtual probate network
                'echo "localip 10.0.0.1" | sudo tee --append /etc/pptpd.conf',  # your server
                'echo "remoteip 10.0.0.100-200" | sudo tee --append /etc/pptpd.conf',  # will be assigned to clients

                # Setup DNS
                'echo "ms-dns 8.8.8.8" | sudo tee --append /etc/ppp/pptpd-options',
                'echo "ms-dns 8.8.4.4" | sudo tee --append /etc/ppp/pptpd-options',

                # Setup authentication for PPTP by adding users and passwords
                'echo "{} pptpd {} *" | sudo tee --append /etc/ppp/chap-secrets'.format(username, password),

                # Restart VPN-server
                'sudo service pptpd restart',

                # Setup Forwarding
                'echo "net.ipv4.ip_forward = 1" | sudo tee --append /etc/sysctl.conf',
                'sudo sysctl -p',

                # Create a NAT rule for iptables
                'sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE',
                'sudo iptables-save',
            ])

            message = 'VPN-server created: {host}. Use username "{username}" and specified password to connect'
            interface.exit_success(message.format(host=instance.public_dns_name, username=username))

        @classmethod
        def terminate(cls):
            """
            Remove EC2-instance with VPN-server
            """

            aws.helpers.delete_instance('vpn')
            aws.helpers.delete_security_group('vpn')
            aws.helpers.delete_key_pair('vpn')