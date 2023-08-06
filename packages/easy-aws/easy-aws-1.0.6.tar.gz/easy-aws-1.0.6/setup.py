import os
import inspect

from setuptools import setup
from setuptools import find_packages


__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))
setup(
    name='easy-aws',
    description='Deploying django-projects to Amazon AWS',
    long_description=open(os.path.join(__location__, 'README.rst')).read(),
    version='1.0.6',

    # The project's main homepage
    url='https://bitbucket.org/dlis/easy-aws',

    # Project license
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Development Status
        'Development Status :: 1 - Planning',

        # Classification
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',

        # License
        'License :: OSI Approved :: MIT License',

        # Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # Relating keywords
    keywords='deploy django amazon aws ec2 elb pycharm',

    # Packages and its data
    packages=find_packages(),
    package_data={'easyaws': ['templates/*']},

    # Requirements
    install_requires=[
        'argparse',
        'paramiko',
        'boto',
        'requests',
    ],

    # Entry points
    entry_points={
        'console_scripts': [
            'easy-aws=easyaws:main',
        ],
    },
)