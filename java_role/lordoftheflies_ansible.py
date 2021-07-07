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

import logging
import os
import os.path
import subprocess
import sys

from java_role import utils

DEFAULT_CONFIG_PATH = "/etc/lordoftheflies"

CONFIG_PATH_ENV = "LORDOFTHEFLIES_CONFIG_PATH"

DEFAULT_VENV_PATH = "venvs/lordoftheflies-ansible"

VENV_PATH_ENV = "LORDOFTHEFLIES_VENV_PATH"

LOG = logging.getLogger(__name__)


def add_args(parser):
    """Add arguments required for running Kolla Ansible to a parser."""
    # $LORDOFTHEFLIES_CONFIG_PATH or /etc/lordoftheflies.
    default_config_path = os.getenv(CONFIG_PATH_ENV, DEFAULT_CONFIG_PATH)
    # $LORDOFTHEFLIES_VENV_PATH or $PWD/venvs/lordoftheflies-ansible
    default_venv = os.getenv(VENV_PATH_ENV,
                             os.path.join(os.getcwd(), DEFAULT_VENV_PATH))
    parser.add_argument("--lordoftheflies-config-path", default=default_config_path,
                        help="path to Kolla configuration. "
                             "(default=$%s or %s)" %
                             (CONFIG_PATH_ENV, DEFAULT_CONFIG_PATH))
    parser.add_argument("-ke", "--lordoftheflies-extra-vars", metavar="EXTRA_VARS",
                        action="append",
                        help="set additional variables as key=value or "
                             "YAML/JSON for Kolla Ansible")
    parser.add_argument("-ki", "--lordoftheflies-inventory", metavar="INVENTORY",
                        help="specify inventory host path "
                             "(default=$%s/inventory or %s/inventory) or "
                             "comma-separated host list for Kolla Ansible" %
                             (CONFIG_PATH_ENV, DEFAULT_CONFIG_PATH))
    parser.add_argument("-kl", "--lordoftheflies-limit", metavar="SUBSET",
                        help="further limit selected hosts to an additional "
                             "pattern")
    parser.add_argument("--lordoftheflies-skip-tags", metavar="TAGS",
                        help="only run plays and tasks whose tags do not match"
                             "these values in Kolla Ansible")
    parser.add_argument("-kt", "--lordoftheflies-tags", metavar="TAGS",
                        help="only run plays and tasks tagged with these "
                             "values in Kolla Ansible")
    parser.add_argument("--lordoftheflies-venv", metavar="VENV", default=default_venv,
                        help="path to virtualenv where Kolla Ansible is "
                             "installed (default=$%s or $PWD/%s)" %
                             (VENV_PATH_ENV, DEFAULT_VENV_PATH))


def _get_inventory_path(parsed_args, inventory_filename):
    """Return the path to the Kolla inventory."""
    if parsed_args.lordoftheflies_inventory:
        return parsed_args.lordoftheflies_inventory
    else:
        return os.path.join(parsed_args.lordoftheflies_config_path, "inventory",
                            inventory_filename)


def _validate_args(parsed_args, inventory_filename):
    """Validate JavaRole Ansible arguments."""
    result = utils.is_readable_dir(parsed_args.lordoftheflies_config_path)
    if not result["result"]:
        LOG.error("Kolla configuration path %s is invalid: %s",
                  parsed_args.lordoftheflies_config_path, result["message"])
        sys.exit(1)

    inventory = _get_inventory_path(parsed_args, inventory_filename)
    result = utils.is_readable_file(inventory)
    if not result["result"]:
        LOG.error("Kolla inventory %s is invalid: %s",
                  inventory, result["message"])
        sys.exit(1)

    result = utils.is_readable_dir(parsed_args.lordoftheflies_venv)
    if not result["result"]:
        LOG.error("Kolla virtualenv %s is invalid: %s",
                  parsed_args.lordoftheflies_venv, result["message"])
        sys.exit(1)


def build_args(parsed_args, command, inventory_filename, extra_vars=None,
               tags=None, verbose_level=None, extra_args=None, limit=None):
    """Build arguments required for running Kolla Ansible."""
    venv_activate = os.path.join(parsed_args.lordoftheflies_venv, "bin", "activate")
    cmd = [".", venv_activate, "&&"]
    cmd += ["lordoftheflies-ansible", command]
    if verbose_level:
        cmd += ["-" + "v" * verbose_level]
    if parsed_args.vault_password_file:
        cmd += ["--key", parsed_args.vault_password_file]
    inventory = _get_inventory_path(parsed_args, inventory_filename)
    cmd += ["--inventory", inventory]
    if parsed_args.lordoftheflies_config_path != DEFAULT_CONFIG_PATH:
        cmd += ["--configdir", parsed_args.lordoftheflies_config_path]
        cmd += ["--passwords",
                os.path.join(parsed_args.lordoftheflies_config_path, "passwords.yml")]
    if parsed_args.lordoftheflies_extra_vars:
        for extra_var in parsed_args.lordoftheflies_extra_vars:
            cmd += ["-e", extra_var]
    if extra_vars:
        for extra_var_name, extra_var_value in extra_vars.items():
            cmd += ["-e", "%s=%s" % (extra_var_name, extra_var_value)]
    if parsed_args.lordoftheflies_limit or limit:
        limits = [l for l in [parsed_args.lordoftheflies_limit, limit] if l]
        cmd += ["--limit", ":&".join(limits)]
    if parsed_args.lordoftheflies_skip_tags:
        cmd += ["--skip-tags", parsed_args.lordoftheflies_skip_tags]
    if parsed_args.lordoftheflies_tags or tags:
        all_tags = [t for t in [parsed_args.lordoftheflies_tags, tags] if t]
        cmd += ["--tags", ",".join(all_tags)]
    if extra_args:
        cmd += extra_args
    return cmd


def run(parsed_args, command, inventory_filename, extra_vars=None,
        tags=None, quiet=False, verbose_level=None, extra_args=None,
        limit=None):
    """Run a Kolla Ansible command."""
    _validate_args(parsed_args, inventory_filename)
    cmd = build_args(parsed_args, command,
                     inventory_filename=inventory_filename,
                     extra_vars=extra_vars, tags=tags,
                     verbose_level=verbose_level,
                     extra_args=extra_args,
                     limit=limit)
    try:
        utils.run_command(" ".join(cmd), quiet=quiet, shell=True)
    except subprocess.CalledProcessError as e:
        LOG.error("lordoftheflies-ansible %s exited %d", command, e.returncode)
        sys.exit(e.returncode)


def run_seed(*args, **kwargs):
    """Run a Kolla Ansible command using the seed inventory."""
    return run(*args, inventory_filename="seed", **kwargs)


def run_overcloud(*args, **kwargs):
    """Run a Kolla Ansible command using the overcloud inventory."""
    return run(*args, inventory_filename="overcloud", **kwargs)
