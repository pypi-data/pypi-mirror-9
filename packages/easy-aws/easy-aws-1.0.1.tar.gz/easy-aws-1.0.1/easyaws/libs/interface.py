import random
import sys
import logging


logger = logging.getLogger(__name__)


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
        print('\t[{position}] {title}'.format(
            position=position,
            title=title(choice) if title else str(choice)
        ))

    # Wait for choice
    while True:
        try:
            selected = int(input('Ваш вариант: '))
            return choices[selected]

        # Incorrect value
        except ValueError:
            continue

        # Index is not from the list
        except IndexError:
            continue

        except KeyboardInterrupt:
            print()
            sys.exit(1)


def confirm():
    """
    Ask for confirmation

    :return: True or False
    """

    code = random.randint(100, 999)
    message = 'Please enter {code} as confirmation code: '.format(code=code)

    # Wait for code been correct
    while True:
        try:
            if code == int(input(message)):
                return True

        # Incorrect value
        except ValueError:
            continue

        except KeyboardInterrupt:
            print()
            sys.exit(1)


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
        print()
        sys.exit(1)

    # Return answer or default
    return answer or default