import sys
import socket
import tempfile
import string
import time
import logging

import pkg_resources
import paramiko
import paramiko.ssh_exception


logger = logging.getLogger(__name__)


class ClientError(BaseException):
    """
    Exception for this module
    """

    def __init__(self, message):
        """
        :type message: str
        :param message: error message
        """

        self.message = message
        logger.critical(self.message)


class Client:
    """
    Client for tasks via SSH
    """

    def __init__(self, url, username='ubuntu', key_path=None, replacements=None, timeout=30):
        """
        Connect to remote host

        :type url: str
        :param url: remote host

        :type username: str
        :param username: username

        :type key_path: str
        :param key_path: path to a file of the key

        :type replacements: dict
        :param replacements: dictionary to replacement in commands and files

        :type timeout: int
        :param timeout: timeout in seconds

        :return: API
        """

        self.__replacements = replacements or dict()

        logger.info('Connect to "{username}@{url}" via SSH'.format(username=username, url=url))

        logger.debug('Wait for 22 port to be opened')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        while sock.connect_ex((url, 22)) is not 0:
            time.sleep(1)

        logger.debug('Establish connection')
        self.__client = paramiko.SSHClient()
        self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.__client.connect(url, username=username, timeout=timeout, key_filename=key_path)
        except socket.timeout:
            raise ClientError('Stopped on timeout in {} seconds'.format(timeout))
        except paramiko.ssh_exception.AuthenticationException:
            raise ClientError('Authentication error')

    def run_command(self, command, timeout=30):
        """
        Execute command on the remote host

        :type command: str
        :param command: command

        :type timeout: int
        :param timeout: timeout in seconds
        """

        # Make replacement
        command = command.format(**self.__replacements)
        logger.debug('$ {}'.format(command))

        try:
            # Send command without blocking and redirect stderr to stdout and wait for completion
            stdin, stdout, stderr = self.__client.exec_command(command + ' 2>&1', timeout=timeout)
            time.sleep(0.1)
            while not stdout.channel.exit_status_ready():
                time.sleep(1)
        except socket.timeout:
            logger.critical('Stopped on timeout in {} seconds'.format(timeout))
            sys.exit(1)

        if stdout.channel.exit_status != 0:
            print(''.join(stdout.readlines()))
            raise ClientError('Command completed with error')

    def run_commands(self, commands):
        """
        Executes list of commands

        :type commands: list
        :param commands: list of commands
        """

        logger.info('Execute {} commands on the remote host'.format(len(commands)))
        for command in commands:
            self.run_command(command)

    def put_files(self, files):
        """
        Put files from local filesystem to the remote host, produces automatic variable replacement.

        Rules for replacements:
            $PROJECT_PATH
                or
            ${PROJECT_PATH}

        Example:
            files = [
                ('templates/supervisord.conf', '/tmp/my.supervisord.conf'),
                ('templates/gunicorn.conf.py', '{PROJECT_PATH}/gunicorn.conf.py'),
                ('/absolute/path/file.py', '/tmp/file.py'),
            ]
            ssh.put_files(files)

        :type files: list
        :param files: list, eg. [('templates/gunicorn.conf.py', '{PROJECT_PATH}/gunicorn.conf.py'), ...]
        """

        logger.info('Put {} files to the remote host'.format(len(files)))
        sftp = self.__client.open_sftp()
        for (source_path, remote_path) in files:
            # Convert relative path of the source file to absolute path
            if not str(source_path).startswith('/'):
                source_path = pkg_resources.resource_filename('easyaws', source_path)

            logger.debug('{} -> {}'.format(source_path, remote_path))
            try:
                # Try to read content of the source file
                source_content = open(source_path).read()
            except UnicodeDecodeError:
                # Can't read content (eg. it is a zipped tar-archive)
                pass
            else:
                # Create new content based on the template after replacement
                template = string.Template(source_content)
                new_content = template.safe_substitute(**self.__replacements)
                if source_content != new_content:
                    # Create temp file
                    tmp = tempfile.NamedTemporaryFile(delete=False)
                    tmp.write(new_content.encode('utf-8') + b'\n')
                    tmp.close()
                    # Change source path to the created temp file
                    source_path = tmp.name

            # Put the source file to the remote host
            try:
                sftp.put(source_path, remote_path)
            except FileNotFoundError:
                raise ClientError('Error in the remote path')

        # Close connection
        sftp.close()

    def apt_install(self, packages):
        """
        Install packages via apt-get

        :type packages: list
        :param packages: list of packages
        """

        commands = ['sudo apt-get update',
                    'sudo apt-get install {} -y'.format(' '.join(packages))]

        for command in commands:
            try:
                self.run_command(command)
            except ClientError:
                # Try again on error
                self.run_command(command)

    def __del__(self):
        self.__client.close()