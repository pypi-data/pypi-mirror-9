import sys
import random
import logging


logger = logging.getLogger(__name__)


class colors:
    """
    ASCII colors
    """

    white_on_green = '\033[1;37;42m'
    white_on_red = '\033[1;37;41m'
    bold = '\033[1m'
    underline = '\033[4m'
    default = '\033[0m'


def select(message, choices, title=None):
    """
    Show choices and offer to choose one of them

    :type message: str
    :param message: message

    :type choices: list
    :param choices: list of choices

    :type title: callable
    :param title: lambda-function for formatting title of a choice

    :return: choice
    """

    if len(choices) == 0:
        logger.debug('Nothing to choose')

    elif len(choices) == 1:
        logger.debug('Only one choice found')
        return choices[0]

    # Print message and choices
    print('{}:'.format(message))
    for (position, choice) in list(enumerate(choices)):
        print('\t{colors.bold}[{position}]{colors.default} {title}'.format(
            colors=colors,
            position=position,
            title=title(choice) if title else str(choice)
        ))

    # Wait for choice
    while True:
        try:
            selected = int(input('Your choice: '))
            return choices[selected]

        # Incorrect value
        except ValueError:
            continue

        # Index is not from the list
        except IndexError:
            continue

        except KeyboardInterrupt:
            exit_error('Interrupt')


def confirm():
    """
    Ask random code for confirmation

    :return: True or False
    """

    code = random.randint(100, 999)
    message = 'Please enter {colors.bold}{code}{colors.default} ' \
              'for confirmation: '.format(code=code, colors=colors)

    # Wait for code been correct
    while True:
        try:
            if code == int(input(message)):
                return True

        # Incorrect value
        except ValueError:
            continue

        except KeyboardInterrupt:
            exit_error('Interrupt')


def request(message, default=None):
    """
    Request input and return answer

    :type message: str
    :param message: Message

    :type default: str
    :param default: Default answer

    :return: answer or default
    """

    # Add default if need
    message += ' [{}]: '.format(default) if default else ': '
    try:
        answer = input(message)
    except KeyboardInterrupt:
        exit_error('Interrupt')

    # Return answer or default
    return answer or default


def print_task(message):
    """
    Print task

    :type message: str
    :param message: message
    """

    print('\n' + colors.underline + message + colors.default + '\n')


def exit_success(message='Success'):
    """
    Exit with success code

    :param message: str
    :param message: message
    """

    print('\n' + colors.white_on_green + message + colors.default + '\n')
    sys.exit(0)


def exit_error(message='Error'):
    """
    Exit with error code

    :type message: str
    :param message: message
    """

    print('\n' + colors.white_on_red + message + colors.default + '\n')
    sys.exit(1)