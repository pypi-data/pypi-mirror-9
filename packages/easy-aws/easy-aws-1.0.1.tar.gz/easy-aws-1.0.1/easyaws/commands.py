import os
import re
import sys
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

        logger.debug('Try to find django project on the path: {}'.format(self.project_path))

        # Check manage.py
        if not os.path.isfile(self.manage_path):
            print('File manage.py is not found')
            sys.exit(1)
        self.project_path = os.getcwd()
        logger.debug('File manage.py is found')

        # Find name of the django project
        with open(self.manage_path, 'r') as manage:
            pattern = r'"(\w+)\.settings"'
            result = re.search(pattern, manage.read())
            if not result:
                print('Name of the django project is not found in manage.py')
                sys.exit(1)
        self.project_name = result.group(1)
        logger.debug('Name of the project is "{}"'.format(self.project_name))

        # Check wsgi.py
        self.wsgi_path = os.path.join(self.project_path, self.project_name, 'wsgi.py')
        if not os.path.isfile(self.wsgi_path):
            print('File wsgi.py is not found in the project directory')
            sys.exit(1)
        logger.debug('File manage.py is found')

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
            logger.critical('Unsupported archive format: {}'.format(archive_format))
            sys.exit(1)

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
        Configure boto
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
    def clean(cls):
        """
        Full clean AWS cloud
        """

        # Request confirmation
        if not interface.confirm():
            return

        # Remove all auto scaling groups
        for group in aws.connections.autoscale.get_all_groups():
            aws.helpers.delete_auto_scaling_group(group.name)

        # Remove all launch configurations
        for config in aws.connections.autoscale.get_all_launch_configurations():
            aws.helpers.delete_launch_configuration(config.name)

        # Remove all load balancers
        for balancer in aws.connections.elb.get_all_load_balancers():
            aws.helpers.delete_load_balancer(balancer.name)

        # Remove all images
        for image in aws.helpers.get_all_images():
            aws.helpers.delete_image(image)

        # Remove all instances
        for instance in aws.helpers.get_all_instances():
            aws.helpers.delete_instance(instance)

        # Remove all keys
        for key in aws.connections.ec2.get_all_key_pairs():
            aws.helpers.delete_key_pair(key.name)

        # Remove all security groups
        for security_group in aws.connections.ec2.get_all_security_groups():
            if security_group.name == 'default':
                continue
            aws.helpers.delete_security_group(security_group.name)

    class Project:
        """
        Deploy django project
        """

        @classmethod
        def push(cls):
            """
            Create image based on the instance with django project
            """

            # Find django project
            django_project = FindDjangoProject()

            # Create security group
            security_group = aws.helpers.get_or_create_security_group('develop', [22, 80])

            # Create key pair
            key_pair = aws.helpers.get_or_create_key_pair('develop')

            # Create unnamed instance
            instance = aws.helpers.create_instance(
                key_pair.name,
                security_group.name,
                aws.helpers.find_last_ubuntu_image_id('14.04'))

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

                # Install apt requirements
                '[ -f {PROJECT_PATH}/requirements-apt.txt ]'
                ' && xargs sudo apt-get install -y < {PROJECT_PATH}/requirements-apt.txt'
                ' || echo skip',

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
                client.apt_install(packages)
                client.run_commands(receipt)

                # Check availability of the instance
                aws.helpers.wait_host(instance.public_dns_name)

                # Create image based on the instance
                image_name = '{project_name}-{timestamp}'.format(
                    project_name=django_project.aws_name,
                    timestamp=time.strftime('%Y.%m.%d-%H.%M'))
                aws.helpers.create_image(image_name, instance)

            finally:
                # Remove instance
                aws.helpers.delete_instance(instance, wait=False)

        @classmethod
        def deploy(cls):
            """
            Deploy image as auto scaling group
            """

            # Find django project
            django_project = FindDjangoProject()

            # Select image
            images = aws.helpers.get_all_images(filters={'name': django_project.aws_name + '*'}, reverse=True)
            image = interface.select('Please select image', images, title=lambda img: img.name or img.id)
            if not image:
                print('There are no images in the your cloud')
                sys.exit(1)

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

        @classmethod
        def undeploy(cls):
            """
            Undeploy image (remove auto scaling group, launch configuration, etc)
            """

            # Find django project
            django_project = FindDjangoProject()

            # Remove auto scaling group
            aws.helpers.delete_auto_scaling_group(django_project.aws_name)

            # Remove launch configuration
            aws.helpers.delete_launch_configuration(django_project.aws_name)

    class Renv:
        """
        Remote environment
        """

        @classmethod
        def create(cls):
            """
            Create EC2-instance for remote environment
            """

            # Create security group
            group = aws.connections.ec2.create_security_group('remote-environment', 'Remote environment')
            group.authorize('tcp', 22, 22, '0.0.0.0/0')

            # Create key
            key = aws.helpers.get_or_create_key_pair('remote-environment')

            # Create instance
            instance = aws.helpers.create_instance(
                key.name,
                group.name,
                aws.helpers.find_last_ubuntu_image_id('14.04'),
                name='remote-environment')

            # Connect to the instance via SSH
            key_path = aws.helpers.generate_path_to_key_pair(key.name)
            client = ssh.Client(instance.public_dns_name, key_path=key_path)

            # Configure the instance
            packages = ['python-pip', 'python3-dev', 'build-essential']
            client.apt_install(packages)

            # Show its url
            print('ssh://ubuntu@' + instance.public_dns_name)

        @classmethod
        def delete(cls):
            """
            Remove instance for remote environment
            """

            # Remove instance
            aws.helpers.delete_instance('remote-environment')

            # Remove key
            aws.helpers.delete_key_pair('remote-environment')

            # Remove security group
            aws.connections.ec2.delete_security_group('remote-environment')