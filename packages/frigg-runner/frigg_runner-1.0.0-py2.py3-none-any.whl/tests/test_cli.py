# -*- coding: utf-8 -*-
import unittest

import mock
from click.testing import CliRunner

from frigg_runner.cli import main


@mock.patch('frigg_runner.runner.Runner.__init__')
@mock.patch('frigg_runner.runner.Runner.run')
class CLITestCase(unittest.TestCase):
    """
    This class tests the cli module.
    """

    def setUp(self):
        self.runner = CliRunner()

    def test_run(self, mock_run, mock_runner):
        self.runner.invoke(main)
        mock_run.assert_called_once()
        mock_runner.assert_called_once_with(failfast=False, verbose=False, path=None)

    def test_run_with_failfast(self, mock_run, mock_runner):
        self.runner.invoke(main, ['--failfast'])
        mock_run.assert_called_once()
        mock_runner.assert_called_once_with(failfast=True, verbose=False, path=None)

    def test_run_with_verbose(self, mock_run, mock_runner):
        self.runner.invoke(main, ['--verbose'])
        mock_run.assert_called_once()
        mock_runner.assert_called_once_with(failfast=False, verbose=True, path=None)

    def test_run_with_path(self, mock_run, mock_runner):
        self.runner.invoke(main, ['--path', '/tmp'])
        mock_run.assert_called_once()
        mock_runner.assert_called_once_with(failfast=False, verbose=False, path='/tmp')
