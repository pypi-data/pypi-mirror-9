from setuptools import setup
from setuptools import find_packages


setup(
    name='easy-aws',
    description='Deploying django-projects to Amazon AWS',
    long_description='Package for easy deploying django-projects to Amazon AWS',
    version='1.0.1',

    # The project's main homepage
    url='https://bitbucket.org/dlis/easy-aws',

    # Author details
    author='dlis',
    author_email='lisovsky@gmail.com',

    # Project license
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Development Status
        'Development Status :: 5 - Production/Stable',

        # Classification
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',

        # License
        'License :: OSI Approved :: MIT License',

        # Python versions
        'Programming Language :: Python :: 3.4',
    ],

    # Relating keywords
    keywords='deploy django amazon aws ec2 elb',

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