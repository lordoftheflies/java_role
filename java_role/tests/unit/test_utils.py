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

import subprocess
import unittest

import mock

from java_role import utils


class TestCase(unittest.TestCase):

    @mock.patch.object(utils, "run_command")
    def test_yum_install(self, mock_run):
        utils.yum_install(["package1", "package2"])
        mock_run.assert_called_once_with(["sudo", "yum", "-y", "install",
                                          "package1", "package2"])

    @mock.patch.object(utils, "run_command")
    def test_yum_install_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "command")
        self.assertRaises(SystemExit,
                          utils.yum_install, ["package1", "package2"])

    @mock.patch.object(utils, "run_command")
    def test_galaxy_install(self, mock_run):
        utils.galaxy_install("/path/to/role/file", "/path/to/roles")
        mock_run.assert_called_once_with(["ansible-galaxy", "install",
                                          "--roles-path", "/path/to/roles",
                                          "--role-file", "/path/to/role/file"])

    @mock.patch.object(utils, "run_command")
    def test_galaxy_install_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "command")
        self.assertRaises(SystemExit,
                          utils.galaxy_install, "/path/to/role/file",
                          "/path/to/roles")

    @mock.patch.object(utils, "read_file")
    def test_read_yaml_file(self, mock_read):
        mock_read.return_value = """---
key1: value1
key2: value2
"""
        result = utils.read_yaml_file("/path/to/file")
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})
        mock_read.assert_called_once_with("/path/to/file")

    @mock.patch.object(utils, "read_file")
    def test_read_yaml_file_open_failure(self, mock_read):
        mock_read.side_effect = IOError
        self.assertRaises(SystemExit, utils.read_yaml_file, "/path/to/file")

    @mock.patch.object(utils, "read_file")
    def test_read_yaml_file_not_yaml(self, mock_read):
        mock_read.return_value = "[1{!"
        self.assertRaises(SystemExit, utils.read_yaml_file, "/path/to/file")

    @mock.patch.object(subprocess, "check_call")
    def test_run_command(self, mock_call):
        output = utils.run_command(["command", "to", "run"])
        mock_call.assert_called_once_with(["command", "to", "run"])
        self.assertIsNone(output)

    @mock.patch("java_role.utils.open")
    @mock.patch.object(subprocess, "check_call")
    def test_run_command_quiet(self, mock_call, mock_open):
        mock_devnull = mock_open.return_value.__enter__.return_value
        output = utils.run_command(["command", "to", "run"], quiet=True)
        mock_call.assert_called_once_with(["command", "to", "run"],
                                          stdout=mock_devnull,
                                          stderr=mock_devnull)
        self.assertIsNone(output)

    @mock.patch.object(subprocess, "check_output")
    def test_run_command_check_output(self, mock_output):
        mock_output.return_value = "command output"
        output = utils.run_command(["command", "to", "run"], check_output=True)
        mock_output.assert_called_once_with(["command", "to", "run"])
        self.assertEqual(output, "command output")

    @mock.patch.object(subprocess, "check_call")
    def test_run_command_failure(self, mock_call):
        mock_call.side_effect = subprocess.CalledProcessError(1, "command")
        self.assertRaises(subprocess.CalledProcessError, utils.run_command,
                          ["command", "to", "run"])
