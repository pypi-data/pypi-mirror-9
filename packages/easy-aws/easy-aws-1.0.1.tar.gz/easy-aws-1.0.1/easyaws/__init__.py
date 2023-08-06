#!/usr/bin/env python3
import inspect
import logging
import argparse

from easyaws.commands import Commands


def generate_parsers(parser, klass):
    """
    Generate subparsers based on the class that describes hierarchy of commands

    :type parser: object
    :param parser: parent parser

    :type klass: class
    :param klass: class that describes hierarchy of commands
    """

    # Get list of commands in the class
    commands = [
        (command.lower(), getattr(klass, command))  # (имя команды, объект команды)
        for command in dir(klass) if not command.startswith('__')
    ]

    # Add subparsers
    subparsers = parser.add_subparsers()
    for name, command in commands:
        # Get command description from properties __docstring__ or __doc__
        doc = inspect.getdoc(command)
        doc = doc[0].lower() + doc[1:] if doc else ''
        subparser = subparsers.add_parser(name, help=doc)

        # Method is detected, i.e single command
        if inspect.ismethod(command):
            subparser.set_defaults(command=command)

        # Class is detected, i.e. group of commands
        elif inspect.isclass(command):
            generate_parsers(subparser, command)


def main():
    # Create main parser
    parser = argparse.ArgumentParser(description='Easy deploy to Amazon AWS')
    parser.add_argument('-d', '--debug', action='store_true', help='show debug log messages')
    generate_parsers(parser, Commands)

    # Parse arguments
    args = parser.parse_args()

    # Setup third-party loggers
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('paramiko').setLevel(logging.CRITICAL)

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create console handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG if args.debug else logging.INFO)
    console_formatter = logging.Formatter('{message}', style='{')
    console.setFormatter(console_formatter)

    # Create file handler
    file = logging.FileHandler('/tmp/{}.log'.format(__name__))
    file.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('{asctime} {levelname: <8} {name}: {message}', style='{')
    file.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console)
    logger.addHandler(file)

    # Execute command
    if hasattr(args, 'command'):
        print(inspect.getdoc(args.command))
        args.command()

    # Or show main help
    else:
        parser.print_help()