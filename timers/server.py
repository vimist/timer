from datetime import datetime
import logging
import os
import pickle
import shlex
from socketserver import StreamRequestHandler, UnixStreamServer
import subprocess as sp

from timers import TIMERS
from timers import commands


LOGGER = logging.getLogger(__name__)


class CommandHandler(StreamRequestHandler):
    """Decode commands, execute handlers, encode and send responses.
    """

    def handle(self):
        request = pickle.loads(self.request.recv(4096))
        LOGGER.info('Request: %s', request)

        function_name = request.pop('action')
        function = getattr(
            commands,
            function_name,
            lambda **kwargs: commands.unknown_action(function_name, **kwargs))
        response = function(**request)

        LOGGER.info('Response: %s', response)
        self.wfile.write(pickle.dumps(response))


def server(socket_file, command):
    """Launch the server process.

    Parameters:
        socket_file (str): The path to the socket file to use for communication.
        command (str): The command string to execute when a timer expires.
    """

    with UnixStreamServer(socket_file, CommandHandler) as svr:
        while True:
            if TIMERS:
                next_timer = TIMERS[0]['when'] - datetime.now()

                if next_timer.total_seconds() < 24 * 60 * 60:
                    svr.timeout = next_timer.total_seconds()
                    LOGGER.info(
                        'Waiting %d seconds until "%s" timer',
                        svr.timeout, TIMERS[0]['what'])
                else:
                    svr.timeout = 24 * 60 * 60
                    LOGGER.info('Waiting %d seconds', svr.timeout)
            else:
                svr.timeout = None
                LOGGER.info('No pending timers, waiting for request')

            svr.handle_request()

            if TIMERS and TIMERS[0]['when'] <= datetime.now():
                timer = TIMERS.pop(0)
                shell_quoted_what = shlex.quote(timer['what'])
                sp.run(command.format(
                    description=shell_quoted_what), shell=True)
