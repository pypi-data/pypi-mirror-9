"""
    colorwrap.py

    Wraps a shell command to make unix/ansi escape codes work.

    Usage:
        colorwrap command arg1 arg2

    Usage as a library:
        import colorwrap
        colorwrap.wrap(['command', 'arg1', 'arg2'])
"""

import os
import subprocess
import argparse
import colorama


colorama.init(autoreset=True, convert=True, strip=True)


def wrap(command):
    """
    Wraps a shell call.

    :param command: The command to run as a list (same format as subprocess.check_output).
    :return: The return code of the command.
    """

    os.putenv('TERM', 'ansi')

    try:
        output = subprocess.check_output(command, shell=True)
        ret = 0
    except subprocess.CalledProcessError as e:
        output = e.output
        ret = e.returncode

    print(output.decode('ascii'))
    return ret


def main():
    """
    Main function for when colorwrap.py is executed.
    Parses arguments and wraps the command.
    """

    parser = argparse.ArgumentParser(description='Makes unix color escape codes work on windows.')
    parser.add_argument('command', nargs='+', help='The command to wrap', type=str)
    args = parser.parse_args()
    wrap(args.command)


if __name__ == '__main__':
    main()
