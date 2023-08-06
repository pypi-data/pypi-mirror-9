# uservice-utils
# Copyright (C) 2015 Canonical
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Tests for the logging code."""

import os.path
import subprocess
import sys
import tempfile
from textwrap import dedent

from testtools import TestCase
from testtools.matchers import (
    Contains,
    Equals,
    FileContains,
    Not,
)

import uservice_utils

class LoggingConfigurationTests(TestCase):

    """Tests for the logging configuration functions.

    These tests all spawn subprocesses to examine the effect of the logging
    configuration.

    """
    def run_script(self, script_contents, run_dir):
        testfile = os.path.join(run_dir, 'test.py')
        with open(testfile, 'wt') as test_file:
            test_file.write(script_contents.format(basedir=run_dir))
        pythonpath = os.path.abspath(
            os.path.join(uservice_utils.__file__, '..', '..')
        )
        process = subprocess.Popen(
            [sys.executable, testfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(PYTHONPATH=pythonpath),
        )
        try:
            out, err = process.communicate(timeout=10)
            return process.returncode, out.decode(), err.decode()
        except subprocess.TimeoutExpired:
            process.kill()
            raise

    def test_defaults_to_stderr(self):
        with tempfile.TemporaryDirectory() as run_dir:
            rc, out, err = self.run_script(
                dedent(
                    """
                    import logging
                    from uservice_utils.logging import configure_service_logging

                    configure_service_logging("{basedir}/nonexistant/some.file")
                    logging.info("Hello World")
                    """
                ),
                run_dir
            )
            self.expectThat(rc, Equals(0))
            self.expectThat(err, Contains("Hello World"))

    def test_can_log_to_file(self):
        with tempfile.TemporaryDirectory() as run_dir:
            rc, out, err = self.run_script(
                dedent(
                    """
                    import logging
                    from uservice_utils.logging import configure_service_logging

                    configure_service_logging("{basedir}/logfile")
                    logging.info("Hello World")
                    """
                ),
                run_dir
            )
            self.expectThat(rc, Equals(0))
            self.expectThat(err, Equals(""))
            self.expectThat(out, Equals(""))
            self.assertThat(
                os.path.join(run_dir, 'logfile'),
                FileContains(matcher=Contains("Hello World"))
            )

    def test_silences_requests(self):
        with tempfile.TemporaryDirectory() as run_dir:
            rc, out, err = self.run_script(
                dedent(
                    """
                    import logging
                    from uservice_utils.logging import configure_service_logging

                    configure_service_logging("{basedir}/nonexistant/some.file")
                    logging.getLogger('requests').info("Will not see")
                    logging.getLogger('requests').warning("Will see")
                    """
                ),
                run_dir
            )
            self.expectThat(rc, Equals(0))
            self.expectThat(err, Not(Contains("Will not see")))
            self.expectThat(err, Contains("Will see"))

