========
easy-aws
========

Tool for easy deploying django-projects to Amazon AWS. Just two commands: *easy-aws push* and *easy-aws deploy*

Quick start
===========

Stage 1. Preparing
------------------

1. Install this package::

    pip install easy-aws

2. Configure boto (enter AWS credentials and select region)::

    easy-aws configure

3. (optional) To specify python module dependencies add file *requirements.txt* to django project directory. Example of *requirements.txt*::

    Django
    mock

4. (optional) To specify system dependencies add file *requirements-apt.txt* to django project directory. Specified packages will be install via *apt-get install*. Example of *requirements-apt.txt*::

    python3-dev
    libpq-dev

Stage 2. Deploying process
--------------------------

All commands should be runned in django project directory.

1. Create and setup temporary instance, upload your django project on instance, create image and remove instance::

    easy-aws push

2. Create load balancer, create launch configuration based on the created image and create auto scaling group (auto scaling up to 3 instances when CPU-load > 70)::

    easy-aws deploy

3. (optional) To remove auto scaling group and launch configuration execute::

    easy-aws undeploy
    
4. (optional) To full clean AWS cloud, i.e remove all auto scaling groups, launch configurations, load balancers, images, instances, key pairs and security groups execute::

    easy-aws clean

Other
-----

- Show debug messages, eg::

    easy-aws -d <command>

- Print help, eg::

    easy-aws -h
    easy-aws <command> -h

