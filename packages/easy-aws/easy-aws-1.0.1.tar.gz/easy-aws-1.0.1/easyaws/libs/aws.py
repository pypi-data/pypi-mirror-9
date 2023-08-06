import os
import sys
import time
import logging

import requests
import requests.exceptions
import boto.ec2
import boto.ec2.elb
import boto.ec2.instance
import boto.ec2.autoscale
import boto.ec2.cloudwatch
import boto.ec2.image
import boto.vpc
import boto.exception

from easyaws.libs import interface


logger = logging.getLogger(__name__)


class __Connections:
    """
    Connect to AWS-services via boto and cache these connections
    """

    __cache = dict()
    __services = {
        'ec2': (boto.ec2, 'get_all_regions'),
        'elb': (boto.ec2.elb, 'get_all_load_balancers'),
        'autoscale': (boto.ec2.autoscale, 'get_all_groups'),
        'cloudwatch': (boto.ec2.cloudwatch, 'list_metrics'),
    }

    def __getattr__(self, name):
        """
        Return cached connection to AWS-service or create and cache new connection

        :type name: str
        :param name: name of AWS-service (ec2, elb, autoscale, cloudwatch, etc)

        :return: connection to AWS-service
        """

        if name not in self.__services:
            raise Exception('Unknown service: "{}"'.format(name))

        try:
            if name not in self.__cache:
                # Establish connection
                service = self.__services[name][0]
                region_name = boto.config.get('Boto', 'aws_region_name')
                connection = service.connect_to_region(region_name)

                # Test the connection
                method_name = self.__services[name][1]
                if method_name:
                    getattr(connection, method_name)()

                # Cache the connection
                self.__cache[name] = connection

        except boto.exception.NoAuthHandlerFound:
            logger.critical('Configuration file not found')
            sys.exit(1)

        except boto.exception.EC2ResponseError as e:
            logger.critical(e.message)
            sys.exit(1)

        # Return the connection from cache
        return self.__cache[name]


class helpers:
    """
    Provide helpers for easy manipulation with AWS-services
    """

    __keys_path = os.path.expanduser('~/.ssh/aws')
    __free_tier = {'ec2_instance_type': 't2.micro'}  # Free limits provided by the Free Tier

    @classmethod
    def generate_path_to_key_pair(cls, name):
        """
        Return path to key pair

        :type name: str
        :param name: name of key pair

        :return: path to key pair
        """

        path = os.path.join(cls.__keys_path, '{}.pem'.format(name))
        return path

    @classmethod
    def get_or_create_key_pair(cls, name, save_key_material=True):
        """
        Return existed or new key pair

        :type name: str
        :param name: name of key pair

        :type save_key_material: bool
        :param save_key_material: require to save a key material to a file

        :return: key pair
        """

        logger.debug('Try to get key pair "{}"'.format(name))
        key = connections.ec2.get_key_pair(name)

        if not key:
            logger.debug('Key pair "{}" is not found'.format(name))
            logger.info('Create new key pair "{}"'.format(name))
            key = connections.ec2.create_key_pair(name)

            if save_key_material:
                if not os.path.isdir(cls.__keys_path):
                    logger.debug('Create local directory for key pairs: {}'.format(cls.__keys_path))
                    os.mkdir(cls.__keys_path, 0o0700)

                path = cls.generate_path_to_key_pair(name)
                logger.debug('Save a key material of the key pair "{}" to file: {}'.format(name, path))
                with open(path, 'w') as f:
                    f.write(key.material)
                os.chmod(path, 0o0400)

        return key

    @classmethod
    def delete_key_pair(cls, name):
        """
        Remove key pair from AWS and local filesystem

        :type name: str
        :param name: name of key pair

        :return: result
        """

        key = connections.ec2.get_key_pair(name)
        if not key:
            return False

        logger.info('Remove key pair "{}"'.format(name))
        key.delete()

        path = cls.generate_path_to_key_pair(name)
        if os.path.isfile(path):
            logger.debug('Remove a file of the key pair "{}": {}'.format(name, path))
            os.remove(path)

        return True

    @classmethod
    def get_or_create_security_group(cls, name, public_ports=None):
        """
        Return existed or new security group with open ports

        :type name: str
        :param name: name of security group

        :type public_ports: list
        :param public_ports: list of ports to opening

        :return: security group
        """

        try:
            logger.debug('Try to get security group "{}"'.format(name))
            group = connections.ec2.get_all_security_groups([name])[0]
        except boto.exception.EC2ResponseError as e:
            if e.error_code == 'InvalidGroup.NotFound':
                logger.info('Create security group "{}"'.format(name))
                group = connections.ec2.create_security_group(name, '-')
            else:
                logger.critical(e.message)
                sys.exit(1)

        # Open specified ports
        if public_ports:
            for port in public_ports:
                try:
                    logger.info('Open for all {} port in the security group "{}"'.format(port, name))
                    group.authorize('tcp', port, port, '0.0.0.0/0')
                except boto.exception.EC2ResponseError as e:
                    if e.error_code == 'InvalidPermission.Duplicate':
                        logger.debug('This port is already open')
                        continue
                    else:
                        logger.critical(e.message)
                        sys.exit(1)

        return group

    @classmethod
    def delete_security_group(cls, name):
        """
        Remove security group

        :type name: str
        :param name: name of security group

        :return: result
        """

        try:
            logger.debug('Try to get security group "{}"'.format(name))
            group = connections.ec2.get_all_security_groups([name])[0]
        except boto.exception.EC2ResponseError as e:
            if e.error_code == 'InvalidGroup.NotFound':
                return False
            else:
                logger.critical(e.message)
                sys.exit(1)

        logger.info('Remove security group "{}"'.format(name))
        group.delete()
        return True

    @classmethod
    def create_instance(cls, key_name, group_name, image_id, instance_type=None, name=None):
        """
        Create new EC2-instance and save its name in the tag "name" if specified

        :type key_name: str
        :param key_name: name of key pair

        :type group_name: str
        :param group_name: name of security group

        :type image_id: str
        :param image_id: image id

        :type instance_type: str
        :param instance_type: type of instance

        :type name: str or None
        :param name: name of instance

        :return: result
        """

        if name and cls.get_instance(name):
            logger.critical('The instance "{}" is already exists'.format(name))
            sys.exit(1)

        try:
            logger.info('Create new EC2-instance "{}" based on the image "{}"'.format(name or 'unnamed', image_id))
            reservation = connections.ec2.run_instances(
                image_id,
                key_name=key_name,
                instance_type=instance_type or cls.__free_tier['ec2_instance_type'],
                monitoring_enabled=True,
                security_group_ids=[group_name])
            instance = reservation.instances[0]
        except boto.exception.EC2ResponseError as e:
            if e.error_code == 'InvalidAMIID.NotFound':
                logger.critical('Image with id "{}" is not found'.format(image_id))
            else:
                logger.critical(e.message)
            sys.exit(1)
        if name:
            logger.debug('Save name "{}" of the instance to the tag "name"'.format(name))
            instance.add_tag('name', name)

        # Remember instance id
        instance_id = instance.id

        # Wait instance
        logger.debug('Wait for the instance to be running')
        while True:
            instance = cls.get_instance(instance_id)
            if instance and instance.state == 'running':
                break
            time.sleep(1)
        logger.debug('The instance is running')
        logger.debug('Wait for the instance to be available')
        while True:
            status = cls.get_instance_status(instance_id)
            if status and 'initializing' not in [status.system_status.status, status.instance_status.status]:
                break
            time.sleep(1)
        logger.debug('The instance is available')

        # Reload and return
        return cls.get_instance(instance, reload_from_aws=True)

    @classmethod
    def get_all_instances(cls, instance_ids=None, filters=None):
        """
        Return all alive instances

        :type instance_ids: list
        :param instance_ids: list of instance ids

        :type filters: dict
        :param filters: dictionary of filters

        :return: list of instances
        """

        # Get list of all instances
        reservations = connections.ec2.get_all_instances(instance_ids=instance_ids, filters=filters)
        all_instances = [reservation.instances for reservation in reservations]

        # Filter alive only
        alive_instances = [instance for instance in sum(all_instances, []) if instance.state != 'terminated']
        logger.debug('{alive} alive found from {all} instances'.format(
            alive=len(alive_instances),
            all=len(all_instances)))

        # Return alive instances
        return alive_instances

    @classmethod
    def get_instance(cls, lookup, reload_from_aws=False):
        """
        Return instance

        :type lookup: mixed
        :param lookup: instance, or its id, or its name

        :type reload_from_aws: bool
        :param reload_from_aws: require to reload image object from AWS

        :return: instance or None
        """

        if isinstance(lookup, str):
            # Try to find by name
            response = cls.get_all_instances(filters={'tag:name': lookup})
            if len(response) > 1:
                logger.critical('More than one instance found by name "{}"'.format(lookup))
                sys.exit(1)
            elif len(response) == 1:
                logger.debug('Instance is found by name "{}"'.format(lookup))
                return response[0]

            # Try to find by id
            response = cls.get_all_instances(instance_ids=[lookup])
            if len(response) == 1:
                logger.debug('Instance is found by id "{}"'.format(lookup))
                return response[0]

            logger.debug('Instance is not found by "{}"'.format(lookup))
            return None

        elif isinstance(lookup, boto.ec2.instance.Instance):
            # Reload if need
            return cls.get_instance(lookup.id) if reload_from_aws else lookup

        else:
            raise Exception('Unknown argument type: {}'.format(type(lookup)))

    @classmethod
    def get_instance_status(cls, instance_id):
        """
        Get instance status

        :type instance_id: str
        :param instance_id: instance id

        :return: instance status or None
        """

        response = connections.ec2.get_all_instance_status(instance_ids=[instance_id])
        return response[0] if response else None

    @classmethod
    def delete_instance(cls, instance, wait=True):
        """
        Remove EC2-instance

        :type instance: str or object
        :param instance: instance, or its name, or its id

        :type wait: bool
        :param wait: require to wait for instance to be terminated

        :return: result
        """

        instance = cls.get_instance(instance)
        name = getattr(instance.tags, 'name', None)

        logger.info('Terminate instance "{}"'.format(name or instance.id))
        connections.ec2.terminate_instances(instance_ids=[instance.id])

        if not wait:
            logger.debug('Do not wait for the termination of the instance "{}"'.format(name or instance.id))
            return None

        logger.debug('Wait for the instance "{}" to be terminated'.format(name or instance.id))
        while instance.state != 'terminated':
            time.sleep(1)
            instance.update()

        return True

    @classmethod
    def create_image(cls, name, instance):
        """
        Create new image from the instance

        :type instance: str or object
        :param instance: instance, or its name, or its id

        :return: image
        """

        instance = cls.get_instance(instance)
        instance_name = getattr(instance.tags, 'name', None)

        logger.info('Create image "{}" from the instance "{}"'.format(name, instance_name or instance.id))
        image_id = connections.ec2.create_image(instance.id, name)

        logger.debug('Wait for the image to be saved "{}"'.format(name))
        image = cls.get_image(image_id)
        while image.state == 'pending':
            time.sleep(1)
            image.update()

        return image

    @classmethod
    def get_image(cls, lookup, reload_from_aws=True):
        """
        Return image

        :type lookup: str or object
        :param lookup: image, or its name, or its id

        :type reload_from_aws: bool
        :param reload_from_aws: require to reload image object from AWS

        :return: image or None
        """

        if isinstance(lookup, boto.ec2.image.Image):
            image = cls.get_image(lookup.id) if reload_from_aws else lookup

        elif isinstance(lookup, str) and connections.ec2.get_image(lookup):
            logger.debug('The image is obtained by its id')
            image = connections.ec2.get_image(lookup)

        elif isinstance(lookup, str) and len(connections.ec2.get_all_images(owners=['self'], filters={'name': lookup})):
            logger.debug('The image is obtained by its name')
            image = connections.ec2.get_all_images(owners=['self'], filters={'name': lookup})[0]

        elif isinstance(lookup, str):
            logger.debug('The image "{}" is not found'.format(lookup))
            image = None

        else:
            raise Exception('Unknown argument type: {}'.format(type(lookup)))

        return image

    @classmethod
    def get_all_images(cls, owners=None, filters=None, reverse=False):
        """
        Return all images

        :type filters: dict
        :param filters: filters

        :return: images list
        """

        # Get images
        images = connections.ec2.get_all_images(owners=owners or ['self'], filters=filters)

        # Sort images by name
        images.sort(key=lambda img: img.name, reverse=reverse)

        # Return images
        return images

    @classmethod
    def find_last_ubuntu_image_id(cls, version):
        """
        Find fresh ubuntu image

        :type version: str
        :param version: version, eg. '14.04'

        :return: image id
        """

        cache_id = '/tmp/easy-aws-last-ubuntu-ami'

        logger.debug('Try to find fresh ubuntu {} image via boto'.format(version))
        name = 'ubuntu*hvm*ssd*{version}*'.format(version=version)
        images = cls.get_all_images(
            owners=['099720109477'],  # Canonical id
            filters={'name': name},
            reverse=True)

        if len(images) > 0:
            image_id = images[0].id

        else:
            logger.warning('Can not find any ubuntu image')
            # Try to find last used image
            last_id = open(cache_id).read() if os.path.isfile(cache_id) else None
            # Request image
            image_id = interface.request('Please enter image id', last_id)

        # Save image id to cache and return it
        with open(cache_id, 'w') as f:
            f.write(image_id)
        return image_id

    @classmethod
    def delete_image(cls, lookup):
        """
        Remove image

        :type lookup: str or object
        :param lookup: image, or its name, or its id

        :return: result
        """

        image = cls.get_image(lookup)
        if not image:
            return False

        logger.info('Remove image "{}"'.format(image.name or image.id))
        image.deregister(delete_snapshot=True)
        return True

    @classmethod
    def create_load_balancer(cls, name, security_group, listeners):
        """
        Create load balancer or return already created

        :type name: str
        :param name: name of load balancer

        :type security_group: str
        :param security_group: name of security group

        :type listeners: list
        :param listeners: listening ports [(80, 80, 'http'), (443, 443, 'tcp')]

        :return: load balancer
        """

        logger.info('Create load balancer "{}"'.format(name))

        # Create or setup security group
        public_ports = [listener[0] for listener in listeners]
        security_group = cls.get_or_create_security_group(security_group, public_ports)

        # Get list of available zones in the current region
        zones = [zone.name for zone in connections.ec2.get_all_zones()]

        # Create new load balancer or get already created
        load_balancer = connections.elb.create_load_balancer(
            name,
            zones,
            security_groups=[security_group.id],
            listeners=listeners,
        )
        health_check = boto.ec2.elb.HealthCheck(target='TCP:80')
        load_balancer.configure_health_check(health_check)

        return load_balancer

    @classmethod
    def delete_load_balancer(cls, name):
        """
        Remove load balancer

        :type name: str
        :param name: name of load balancer

        :return: result
        """

        logger.info('Remove load balancer "{}"'.format(name))

        response = connections.elb.get_all_load_balancers(load_balancer_names=[name])
        if not len(response):
            logger.debug('Load balancer "{}" is not found'.format(name))
            return False
        load_balancer = response[0]
        load_balancer.delete()

        logger.debug('Wait for each connected network interface to be removed')
        while len(connections.ec2.get_all_network_interfaces(filters={'description': 'ELB {}'.format(name)})):
            time.sleep(1)

        return True

    @classmethod
    def create_launch_configuration(cls, name, image_id, key_name, security_group, instance_type=None):
        """
        Create launch configuration

        :type name: str
        :param name: name of launch configuration

        :type image_id: str
        :param image_id: image id

        :type key_name: str
        :param key_name: name of key pair

        :type security_group: str
        :param security_group: name of security group

        :type instance_type: str
        :param instance_type: type of instance

        :return: launch configuration
        """

        security_group = cls.get_or_create_security_group(security_group)

        logger.info('Create launch configuration "{}" based on the image "{}"'.format(name, image_id))
        launch_configuration = boto.ec2.autoscale.LaunchConfiguration(
            name=name,
            image_id=image_id,
            key_name=key_name,
            security_groups=[security_group.id],
            instance_type=instance_type or cls.__free_tier['ec2_instance_type'],
            instance_monitoring=True)
        connections.autoscale.create_launch_configuration(launch_configuration)

        return launch_configuration

    @classmethod
    def delete_launch_configuration(cls, name):
        """
        Remove launch configuration

        :type name: str
        :param name: name of launch configuration

        :return: result
        """

        logger.info('Remove launch configuration "{}"'.format(name))
        response = connections.autoscale.get_all_launch_configurations(names=[name])
        if not len(response):
            return False

        connections.autoscale.delete_launch_configuration(name)
        return True

    @classmethod
    def create_auto_scaling_group(cls, name, load_balancer, launch_configuration, min_size=1, max_size=3):
        """
        Create auto scaling group

        :param name: str
        :param name: name of auto scaling group

        :type load_balancer: str
        :param load_balancer: name of load balancer

        :type launch_configuration: str
        :param launch_configuration: name of launch configuration

        :type min_size: int
        :param min_size: minimum number of instance in the group

        :type max_size: int
        :param max_size: maximum number of instance in the group

        :return: auto scaling group
        """

        logger.info('Create auto scaling group "{}"'.format(name))

        # Get list of available zones in the current region
        zones = [zone.name for zone in connections.ec2.get_all_zones()]

        # Create auto scaling group
        auto_scaling_group = boto.ec2.autoscale.AutoScalingGroup(
            group_name=name,
            load_balancers=[load_balancer],
            availability_zones=zones,
            launch_config=launch_configuration,
            min_size=min_size,
            max_size=max_size)
        connections.autoscale.create_auto_scaling_group(auto_scaling_group)

        # Create scaling policies and send them to AWS
        scale_up_policy = boto.ec2.autoscale.ScalingPolicy(
            name='scale_up',
            adjustment_type='ChangeInCapacity',
            as_name=auto_scaling_group.name,
            scaling_adjustment=1,
            cooldown=180)
        scale_down_policy = boto.ec2.autoscale.ScalingPolicy(
            name='scale_down',
            adjustment_type='ChangeInCapacity',
            as_name=auto_scaling_group.name,
            scaling_adjustment=-1,
            cooldown=180)
        connections.autoscale.create_scaling_policy(scale_up_policy)
        connections.autoscale.create_scaling_policy(scale_down_policy)

        # Get them back to obtain policy arns
        scale_up_policy = connections.autoscale.get_all_policies(
            as_group=auto_scaling_group.name,
            policy_names=['scale_up'])[0]
        scale_down_policy = connections.autoscale.get_all_policies(
            as_group=auto_scaling_group.name,
            policy_names=['scale_down'])[0]

        # Create and register alarms
        alarm_dimensions = {"AutoScalingGroupName": auto_scaling_group.name}
        scale_up_alarm = boto.ec2.cloudwatch.MetricAlarm(
            name='scale_up_on_cpu',
            namespace='AWS/EC2',
            metric='CPUUtilization',
            statistic='Average',
            comparison='>',
            threshold=70,
            period=60,
            evaluation_periods=2,
            alarm_actions=[scale_up_policy.policy_arn],  # connecting scaling policy by arn
            dimensions=alarm_dimensions)
        scale_down_alarm = boto.ec2.cloudwatch.MetricAlarm(
            name='scale_down_on_cpu',
            namespace='AWS/EC2',
            metric='CPUUtilization',
            statistic='Average',
            comparison='<',
            threshold=40,
            period=60,
            evaluation_periods=2,
            alarm_actions=[scale_down_policy.policy_arn],  # connecting scaling policy by arn
            dimensions=alarm_dimensions)
        connections.cloudwatch.create_alarm(scale_up_alarm)
        connections.cloudwatch.create_alarm(scale_down_alarm)

        logger.info('Wait for at least one instance been available in the auto scaling group "{}"'.format(name))
        while True:
            auto_scaling_group = cls.get_auto_scaling_group(name)
            in_service = [i.lifecycle_state == 'InService' for i in auto_scaling_group.instances]
            if any(in_service):
                break
            time.sleep(1)

        return auto_scaling_group

    @classmethod
    def get_auto_scaling_group(cls, name):
        """
        Return auto scaling group

        :type name: str
        :param name: name of auto scaling group

        :return: auto scaling group
        """

        response = connections.autoscale.get_all_groups(names=[name])

        if len(response) == 0:
            return None

        return response[0]

    @classmethod
    def delete_auto_scaling_group(cls, name):
        """
        Remove auto scaling group

        :type name: str
        :param name: name of auto scaling group

        :return: result
        """

        logger.info('Remove the auto scaling group "{}"'.format(name))
        auto_scaling_group = cls.get_auto_scaling_group(name)
        if not auto_scaling_group:
            return False

        # Remove
        auto_scaling_group.delete(force_delete=True)

        logger.debug('Wait for the auto scaling group to be deleted')
        while cls.get_auto_scaling_group(name):
            time.sleep(1)
        return True

    @classmethod
    def wait_host(cls, dns_name):
        """
        Wait for host availability

        :type dns_name: str
        :param dns_name: url, eg. "example.com"
        """

        url = 'http://{}/'.format(dns_name)
        logger.info('Wait for host to be available by url: {}'.format(url))
        while True:
            try:
                # Send HEAD-request to the host
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    break
                time.sleep(1)
            except requests.exceptions.ConnectionError:
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(1)

        logger.debug('Host is available')


def get_regions():
    """
    Return list of available regions for using services

    :return: list
    """

    # Get regions for each service
    ec2_regions = [region.name for region in boto.ec2.regions()]
    foo_regions = ec2_regions[:]  # Example of regions of other service

    # Find intersection
    regions = set(ec2_regions).intersection(foo_regions)

    # Return sorted list
    return sorted(regions)

# Return connections to the AWS-services
connections = __Connections()