import argparse
import logging

from timers.client import client
from timers.server import server


LOGGER = logging.getLogger(__name__)


def main():
    """Main entry point into the program."""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    parser.add_argument(
        '--socket-file', dest='socket_file', default='/tmp/timers.sock',
        help='The phrase to add as a timer')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0, help='Output varying '
            'levels of logging, specify multiple times to increase verbosity')

    server_parser = subparsers.add_parser('server')
    server_parser.set_defaults(handler=server)
    server_parser.add_argument(
        'command', help=(
            'The command to execute for each timer, use {description} to '
            'interpolate timer description. Do not quote {description}, it '
            'will automatically be shell escaped for you'
        ))

    add_parser = subparsers.add_parser('add')
    add_parser.set_defaults(handler=client)
    add_parser.set_defaults(action='add')
    add_parser.add_argument(
        'phrase', nargs='+', help='The phrase to parse and add as a timer')

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(handler=client)
    list_parser.set_defaults(action='list_timers')
    list_parser.add_argument(
        '-p', '--parsable', action='store_true', help='Output the timers in a '
            'format that can be interpreted by `add`. `absolute` and `delta` '
            'options are ignored if this is specified.')
    list_parser.add_argument(
        '-a', '--absolute', action='store_true',
        help='Display the absolute time of the timer')
    list_parser.add_argument(
        '-d', '--delta', action='store_true',
        help='Display the time until the timer is due')

    remove_parser = subparsers.add_parser('remove')
    remove_parser.set_defaults(handler=client)
    remove_parser.set_defaults(action='remove')
    remove_parser.add_argument(
        'timer_index', type=int,
        help='The index of the timer, as returned by `list`')

    args = parser.parse_args()
    args_dict = vars(args)

    # Configure logging
    verbosity = args_dict.pop('verbose')
    level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(verbosity, logging.DEBUG)

    logging.basicConfig(
        level=level, style='{', format='{asctime}  {levelname:8s}  {message}')

    LOGGER.info('Logging level set to %s', logging.getLevelName(level))

    handler = args_dict.pop('handler')
    handler(**args_dict)


if __name__ == '__main__':
    main()
