#!/usr/bin/env python3

import re
from pathlib import (Path,)
import os
import argparse
import subprocess
from typing import (Optional,)


class ProgramOptions(object):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-v', '--verbose', action='count', default=0, help='Verbosity.')

        sub_parsers = parser.add_subparsers(dest='sub_command')

        password_help="A password for authenticated encryption.  Passwords\
 must match between encryption and decryption but must not be disclosed to\
 third person.  Because command line arguments can be read by other users on\
 the same host, passwords must not be specified directly in command line\
 arguments.  Instead, you have the following options; `env:VARNAME' to read\
 the password from the environment variable `VARNAME', `file:FILE' to read the\
 password from the content of the file `FILE' (with any trailing newlines\
 stripped), or `pipe:EXECUTABLE' to read the password from standard output of\
 the program `EXECUTABLE' (with any trailing newlines stripped)."
        key_derivation_iteration_help="The number of iterations of key\
 derivation.  `N_ITERATIONS' must match between encryption and decryption.\
  Larger values result in more secure but slower key derivation."

        encrypt_parser = sub_parsers.add_parser(
            'encrypt', help='Perform authenticated encryption.')
        encrypt_parser.add_argument(
            '-p', '--password', required=True, help=password_help,
            metavar='PASSWORD')
        encrypt_parser.add_argument(
            '--key-derivation-iteration', default=1000000, type=int,
            help=key_derivation_iteration_help, metavar='N_ITERATIONS')
        encrypt_parser.add_argument(
            '-i', '--input', help="Read the data to be encrypted from\
 `INPUT_FILE', or standard input if `INPUT_FILE' is omitted or equal to `-'.",
            metavar='INPUT_FILE')
        encrypt_parser.add_argument(
            '-o', '--output', help="Write the encrypted data to `OUTPUT_FILE',\
 or standard output if `OUTPUT_FILE' is omitted or equal to `-'.",
            metavar='OUTPUT_FILE')

        decrypt_parser = sub_parsers.add_parser(
            'decrypt', help='Decrypt encrypted data, with authentication\
 verified.')
        decrypt_parser.add_argument(
            '-p', '--password', required=True, help=password_help,
            metavar='PASSWORD')
        decrypt_parser.add_argument(
            '--key-derivation-iteration', default=1000000, type=int,
            help=key_derivation_iteration_help, metavar='N_ITERATIONS')
        decrypt_parser.add_argument(
            '-i', '--input', help="Read the encrypted data to be decrypted\
 from \`INPUT_FILE', or standard input if `INPUT_FILE' is omitted or equal to\
 `-'.", metavar='INPUT_FILE')
        decrypt_parser.add_argument(
            '-o', '--output', help="Write the decrypted data to `OUTPUT_FILE',\
 or standard output if `OUTPUT_FILE' is omitted or equal to `-'.",
            metavar='OUTPUT_FILE')

        options = parser.parse_args()

        self._verbosity = min(options.verbose, 2)

        if options.sub_command == 'encrypt':
            self._mode = 'encryption'
        elif options.sub_command == 'decrypt':
            self._mode = 'decryption'
        else:
            raise RuntimeError(
                f'{options.sub_command}: An unknown sub-command.')

        self._password = None
        if options.password.startswith('env:'):
            m = re.search('^env:(.*)$', options.password)
            varname = m[1]
            if varname not in os.environ:
                raise RuntimeError(
                    f'{varname}: No such environment variable exists.')
            self._password = os.environ[varname]
        elif options.password.startswith('file:'):
            m = re.search('^file:(.*)$', options.password)
            password_file_path = Path(m[1])
            if not password_file_path.exists():
                raise RuntimeError(
                    f"{password_file_path}: No such file exists.")
            if not password_file_path.is_file():
                raise CommandLineParseError(
                    f"{password_file_path}: Not a file.")
            with open(password_file_path) as password_file:
                self._password = password_file.read().rstrip('\n')
        elif options.password.startswith('pipe:'):
            m = re.search('^pipe:(.*)$', options.password)
            password_program_path = Path(m[1])
            password_program_run = subprocess.run(
                str(password_program_path), stdin=subprocess.DEVNULL,
                capture_output=True, text=True)
            if password_program_run.returncode != 0:
                raise RuntimeError(
                    f'''Failed to run the specified program.
  args: {password_program_run.args}
  stdout: {password_program_run.stdout}
  stderr: {password_program_run.stderr}
  returncode: {password_program_run.returncode}''')
            self._password = password_program_run.stdout.rstrip('\n')
        if self._password is None:
            raise RuntimeError(
                f'{options.password}: An invalid password specification.')

        if options.key_derivation_iteration < 0:
            raise RuntimeError(
                f'{options.key_derivation_iteration}: An invalid value for'
                ' key derivation iterations.')
        self._key_derivation_iterations = options.key_derivation_iteration

        if options.input in (None, '-'):
            self._input_file_path = None
        else:
            self._input_file_path = Path(options.input)
            if not self._input_file_path.exists():
                raise RuntimeError(
                    f'{self._input_file_path}: No such file exists.')
            if not self._input_file_path.is_file():
                raise RuntimeError(f'{self._input_file_path}: Not a file.')

        if options.output in (None, '-'):
            self._output_file_path = None
        else:
            self._output_file_path = Path(options.output)
            if self._output_file_path.exists():
                raise RuntimeError(
                    f'{self._output_file_path}: File already exists.')

    @property
    def verbosity(self) -> int:
        return self._verbosity

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def password(self) -> str:
        return self._password

    @property
    def key_derivation_iterations(self) -> int:
        return self._key_derivation_iterations

    @property
    def input_file_path(self) -> Optional[Path]:
        return self._input_file_path

    @property
    def output_file_path(self) -> Optional[Path]:
        return self._output_file_path
