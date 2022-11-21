import pickle
import socket
import sys


def client(socket_file, **kwargs):
    """Serialise the given arguments and pass them to the server.

    Also prints the response and sets the exit code.

    Parameters:
        socket_file (str): The path to the socket file to use for communication.
        **kwargs (dict): Arguments needed to execute the given command.
    """
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(socket_file)
        except (FileNotFoundError, ConnectionRefusedError):
            print('timers server not running', file=sys.stderr)
            sys.exit(1)

        sock.sendall(pickle.dumps(kwargs))

        # 4069 bytes is a lot of timers, this shouldn't be an issue for the
        # perceived use case
        response = pickle.loads(sock.recv(4096))

        success = response['status'] == 'success'

        if response.get('message'):
            print(
                response['message'],
                file=sys.stdout if success else sys.stderr)

        sys.exit(0 if success else 1)
