import argparse
import os
import unittest

import mock

from java_role import utils
from java_role import vault


class TestCase(unittest.TestCase):

    def test_validate_args_ok(self):
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        parsed_args = parser.parse_args([])
        vault.validate_args(parsed_args)

    @mock.patch.dict(os.environ, {"JAVA_ROLE_VAULT_PASSWORD": "test-pass"})
    def test_validate_args_env(self):
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        parsed_args = parser.parse_args([])
        vault.validate_args(parsed_args)

    @mock.patch.dict(os.environ, {"JAVA_ROLE_VAULT_PASSWORD": "test-pass"})
    def test_validate_args_ask_vault_pass(self):
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        parsed_args = parser.parse_args(["--ask-vault-pass"])
        self.assertRaises(SystemExit, vault.validate_args, parsed_args)

    @mock.patch.dict(os.environ, {"JAVA_ROLE_VAULT_PASSWORD": "test-pass"})
    def test_validate_args_vault_password_file(self):
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        parsed_args = parser.parse_args(["--vault-password-file",
                                         "/path/to/file"])
        self.assertRaises(SystemExit, vault.validate_args, parsed_args)

    @mock.patch.object(vault.getpass, 'getpass')
    def test__ask_vault_pass(self, mock_getpass):
        mock_getpass.return_value = 'test-pass'

        # Call twice to verify that the user is only prompted once.
        result = vault._ask_vault_pass()
        self.assertEqual('test-pass', result)
        mock_getpass.assert_called_once_with("Vault password: ")

        result = vault._ask_vault_pass()
        self.assertEqual('test-pass', result)
        mock_getpass.assert_called_once_with("Vault password: ")

    @mock.patch.object(utils, 'read_file')
    def test__read_vault_password_file(self, mock_read):
        mock_read.return_value = "test-pass\n"
        result = vault._read_vault_password_file("/path/to/file")
        self.assertEqual("test-pass", result)
        mock_read.assert_called_once_with("/path/to/file")

    def test_update_environment_no_vault(self):
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        parsed_args = parser.parse_args([])
        env = {}
        vault.update_environment(parsed_args, env)
        self.assertEqual({}, env)

    @mock.patch.object(vault, '_ask_vault_pass')
    def test_update_environment_prompt(self, mock_ask):
        mock_ask.return_value = "test-pass"
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        parsed_args = parser.parse_args(["--ask-vault-pass"])
        env = {}
        vault.update_environment(parsed_args, env)
        self.assertEqual({"JAVA_ROLE_VAULT_PASSWORD": "test-pass"}, env)
        mock_ask.assert_called_once_with()

    @mock.patch.object(vault, '_read_vault_password_file')
    def test_update_environment_file(self, mock_read):
        mock_read.return_value = "test-pass"
        parser = argparse.ArgumentParser()
        vault.add_args(parser)
        args = ["--vault-password-file", "/path/to/file"]
        parsed_args = parser.parse_args(args)
        env = {}
        vault.update_environment(parsed_args, env)
        self.assertEqual({"JAVA_ROLE_VAULT_PASSWORD": "test-pass"}, env)
        mock_read.assert_called_once_with("/path/to/file")
