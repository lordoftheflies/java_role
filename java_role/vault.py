#  The MIT License (MIT)
#
#  Copyright (c) 2019 László Hegedűs
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import subprocess

from java_role import utils

VAULT_PASSWORD_ENV = "JAVA_ROLE_VAULT_PASSWORD"


def _get_default_vault_password_file():
    """Return the default value for the vault password file argument.

    It is possible to use an environment variable to avoid typing the vault
    password.
    """
    if not os.getenv(VAULT_PASSWORD_ENV):
        return None
    cmd = ["which", "java_role_vault_password_helper"]
    try:
        output = utils.run_command(cmd, check_output=True)
    except subprocess.CalledProcessError:
        return None
    return output.strip()


def add_args(parser):
    """Add arguments required for running Ansible playbooks to a parser."""
    default_vault_password_file = _get_default_vault_password_file()
    vault = parser.add_mutually_exclusive_group()
    vault.add_argument("--ask-vault-pass", action="store_true",
                       help="ask for vault password")
    vault.add_argument("--vault-password-file", metavar="VAULT_PASSWORD_FILE",
                       default=default_vault_password_file,
                       help="vault password file")


def build_args(parsed_args):
    """Build a list of command line arguments for use with ansible-playbook."""
    cmd = []
    if parsed_args.ask_vault_pass:
        cmd += ["--ask-vault-pass"]
    elif parsed_args.vault_password_file:
        cmd += ["--vault-password-file", parsed_args.vault_password_file]
    return cmd
