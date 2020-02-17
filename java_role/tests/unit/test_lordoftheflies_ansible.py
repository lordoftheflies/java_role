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

import argparse
import os
import subprocess
import unittest

import mock

from java_role import lordoftheflies_ansible
from java_role import utils
from java_role import vault


@mock.patch.object(os, "getcwd", new=lambda: "/path/to/cwd")
class TestCase(unittest.TestCase):

    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run(self, mock_validate, mock_run):
        parser = argparse.ArgumentParser()
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        parsed_args = parser.parse_args([])
        lordoftheflies_ansible.run(parsed_args, "command", "overcloud")
        expected_cmd = [
            ".", "/path/to/cwd/venvs/lordoftheflies-ansible/bin/activate", "&&",
            "lordoftheflies-ansible", "command",
            "--inventory", "/etc/lordoftheflies/inventory/overcloud",
        ]
        expected_cmd = " ".join(expected_cmd)
        mock_run.assert_called_once_with(expected_cmd, shell=True, quiet=False)

    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run_all_the_args(self, mock_validate, mock_run):
        parser = argparse.ArgumentParser()
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        args = [
            "--lordoftheflies-config-path", "/path/to/config",
            "-ke", "ev_name1=ev_value1",
            "-ki", "/path/to/inventory",
            "-kl", "host1:host2",
            "-kt", "tag1,tag2",
        ]
        parsed_args = parser.parse_args(args)
        lordoftheflies_ansible.run(parsed_args, "command", "overcloud")
        expected_cmd = [
            ".", "/path/to/cwd/venvs/lordoftheflies-ansible/bin/activate", "&&",
            "lordoftheflies-ansible", "command",
            "--inventory", "/path/to/inventory",
            "--configdir", "/path/to/config",
            "--passwords", "/path/to/config/passwords.yml",
            "-e", "ev_name1=ev_value1",
            "--limit", "host1:host2",
            "--tags", "tag1,tag2",
        ]
        expected_cmd = " ".join(expected_cmd)
        mock_run.assert_called_once_with(expected_cmd, shell=True, quiet=False)

    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run_all_the_long_args(self, mock_validate, mock_run):
        parser = argparse.ArgumentParser()
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        args = [
            "--ask-vault-pass",
            "--lordoftheflies-config-path", "/path/to/config",
            "--lordoftheflies-extra-vars", "ev_name1=ev_value1",
            "--lordoftheflies-inventory", "/path/to/inventory",
            "--lordoftheflies-limit", "host1:host2",
            "--lordoftheflies-skip-tags", "tag3,tag4",
            "--lordoftheflies-tags", "tag1,tag2",
        ]
        parsed_args = parser.parse_args(args)
        lordoftheflies_ansible.run(parsed_args, "command", "overcloud")
        expected_cmd = [
            ".", "/path/to/cwd/venvs/lordoftheflies-ansible/bin/activate", "&&",
            "lordoftheflies-ansible", "command",
            "--inventory", "/path/to/inventory",
            "--configdir", "/path/to/config",
            "--passwords", "/path/to/config/passwords.yml",
            "-e", "ev_name1=ev_value1",
            "--limit", "host1:host2",
            "--skip-tags", "tag3,tag4",
            "--tags", "tag1,tag2",
        ]
        expected_cmd = " ".join(expected_cmd)
        mock_run.assert_called_once_with(expected_cmd, shell=True, quiet=False)

    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run_vault_password_file(self, mock_validate, mock_run):
        parser = argparse.ArgumentParser()
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        args = [
            "--vault-password-file", "/path/to/vault/pw",
        ]
        parsed_args = parser.parse_args(args)
        lordoftheflies_ansible.run(parsed_args, "command", "overcloud")
        expected_cmd = [
            ".", "/path/to/cwd/venvs/lordoftheflies-ansible/bin/activate", "&&",
            "lordoftheflies-ansible", "command",
            "--key", "/path/to/vault/pw",
            "--inventory", "/etc/lordoftheflies/inventory/overcloud",
        ]
        expected_cmd = " ".join(expected_cmd)
        mock_run.assert_called_once_with(expected_cmd, shell=True, quiet=False)

    @mock.patch.dict(os.environ, {"JAVA_ROLE_VAULT_PASSWORD": "test-pass"})
    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run_vault_password_helper(self, mock_vars, mock_run):
        mock_vars.return_value = []
        parser = argparse.ArgumentParser()
        mock_run.return_value = "/path/to/java_role-vault-password-helper"
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        mock_run.assert_called_once_with(
            ["which", "java_role-vault-password-helper"], check_output=True)
        mock_run.reset_mock()
        parsed_args = parser.parse_args([])
        lordoftheflies_ansible.run(parsed_args, "command", "overcloud")
        expected_cmd = [
            ".", "/path/to/cwd/venvs/lordoftheflies-ansible/bin/activate", "&&",
            "lordoftheflies-ansible", "command",
            "--key", "/path/to/java_role-vault-password-helper",
            "--inventory", "/etc/lordoftheflies/inventory/overcloud",
        ]
        expected_cmd = " ".join(expected_cmd)
        mock_run.assert_called_once_with(expected_cmd, shell=True, quiet=False)

    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run_func_args(self, mock_validate, mock_run):
        parser = argparse.ArgumentParser()
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        args = [
            "--lordoftheflies-extra-vars", "ev_name1=ev_value1",
            "--lordoftheflies-tags", "tag1,tag2",
        ]
        parsed_args = parser.parse_args(args)
        kwargs = {
            "extra_vars": {"ev_name2": "ev_value2"},
            "tags": "tag3,tag4",
            "verbose_level": 1,
            "extra_args": ["--arg1", "--arg2"],
        }
        lordoftheflies_ansible.run(parsed_args, "command", "overcloud", **kwargs)
        expected_cmd = [
            ".", "/path/to/cwd/venvs/lordoftheflies-ansible/bin/activate", "&&",
            "lordoftheflies-ansible", "command",
            "-v",
            "--inventory", "/etc/lordoftheflies/inventory/overcloud",
            "-e", "ev_name1=ev_value1",
            "-e", "ev_name2=ev_value2",
            "--tags", "tag1,tag2,tag3,tag4",
            "--arg1", "--arg2",
        ]
        expected_cmd = " ".join(expected_cmd)
        mock_run.assert_called_once_with(expected_cmd, shell=True, quiet=False)

    @mock.patch.object(utils, "run_command")
    @mock.patch.object(lordoftheflies_ansible, "_validate_args")
    def test_run_failure(self, mock_validate, mock_run):
        parser = argparse.ArgumentParser()
        lordoftheflies_ansible.add_args(parser)
        vault.add_args(parser)
        parsed_args = parser.parse_args([])
        mock_run.side_effect = subprocess.CalledProcessError(1, "dummy")
        self.assertRaises(SystemExit,
                          lordoftheflies_ansible.run, parsed_args, "command",
                          "overcloud")
