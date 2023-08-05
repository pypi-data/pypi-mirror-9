# Copyright (C) 2014  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or modify
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

"""pytest integration with BeakerLib"""

import os
import re
import sys
import traceback
import subprocess

import pytest


def shell_quote(string):
    return "'" + string.replace("'", "'\\''") + "'"


def pytest_addoption(parser):
    parser.addoption(
        '--with-beakerlib', action="store_true",
        dest="with_beakerlib", default=None,
        help="Report test results via beakerlib")


@pytest.mark.tryfirst
def pytest_load_initial_conftests(args, early_config, parser):
    ns = early_config.known_args_namespace
    if ns.with_beakerlib:
        if 'BEAKERLIB' not in os.environ:
            exit('$BEAKERLIB not set, cannot use --with-beakerlib')

        plugin = BeakerLibPlugin()
        pluginmanager = early_config.pluginmanager.register(
            plugin, 'BeakerLibPlugin')


class BeakerLibProcess(object):
    """Manager of a Bash process that is being fed beakerlib commands
    """
    def __init__(self, env=os.environ):
        if 'BEAKERLIB' not in env:
            raise RuntimeError('$BEAKERLIB not set, cannot use BeakerLib')

        self.env = env
        # Set up the Bash process
        self.bash = subprocess.Popen(['bash'],
                                     stdin=subprocess.PIPE,
                                     stdout=open(os.devnull, 'w'),
                                     stderr=open(os.devnull, 'w'))
        source_path = os.path.join(self.env['BEAKERLIB'], 'beakerlib.sh')
        self.run_beakerlib_command(['.', source_path])

    def run_beakerlib_command(self, cmd):
        """Given a command as a Popen-style list, run it in the Bash process"""
        if not self.bash:
            return
        for word in cmd:
            self.bash.stdin.write(shell_quote(word))
            self.bash.stdin.write(' ')
        self.bash.stdin.write('\n')
        self.bash.stdin.flush()
        assert self.bash.returncode is None, "BeakerLib Bash process exited"

    def end(self):
        """End the Bash process"""
        self.run_beakerlib_command(['exit'])
        bash = self.bash
        self.bash = None
        bash.communicate()

    def log_exception(self, err=None):
        """Log an exception

        err is a 3-tuple as returned from sys.exc_info(); if not given,
        sys.exc_info() is used.
        """
        if err is None:
            err = sys.exc_info()
        message = ''.join(traceback.format_exception(*err)).rstrip()
        self.run_beakerlib_command(['rlLogError', message])


class BeakerLibPlugin(object):
    def __init__(self):
        self.process = BeakerLibProcess(env=os.environ)

        self._current_item = None

    def run_beakerlib_command(self, cmd):
        """Given a command as a Popen-style list, run it in the Bash process"""
        self.process.run_beakerlib_command(cmd)

    def get_item_name(self, item):
        """Return a "identifier-style" name for the given item

        The name only contains the characters [^a-zA-Z0-9_].
        """
        bad_char_re = re.compile('[^a-zA-Z0-9_]')
        parts = []
        current = item
        while current:
            if isinstance(current, pytest.Module):
                name = current.name
                if name.endswith('.py'):
                    name = name[:-3]
                name = bad_char_re.sub('-', name)
                parts.append(name)
                break
            if isinstance(current, pytest.Instance):
                pass
            else:
                name = current.name
                name = bad_char_re.sub('-', name)
                parts.append(name)
            current = current.parent
        return '-'.join(reversed(parts))

    def set_current_item(self, item):
        """Set the item that is currently being processed

        No-op if the same item is already being processed.
        Ends the phase for the previous item, if any.
        """
        if item != self._current_item:
            item_name = self.get_item_name(item)
            if self._current_item:
                self.run_beakerlib_command(['rlPhaseEnd'])
            if item:
                self.run_beakerlib_command(['rlPhaseStart', 'FAIL', item_name])
            self._current_item = item

    def pytest_collection_modifyitems(self, session, config, items):
        """Log all collected items at start of test"""
        self.run_beakerlib_command(['rlLogInfo', 'Collected pytest tests:'])
        for item in items:
            self.run_beakerlib_command(['rlLogInfo',
                                        '  - ' + self.get_item_name(item)])

    def pytest_runtest_setup(self, item):
        """Log item before running it"""
        self.set_current_item(item)

    def pytest_runtest_makereport(self, item, call):
        """Report pass/fail for setup/call/teardown of an item"""
        self.set_current_item(item)
        desc = '%s: %s' % (call.when, item)

        if not call.excinfo:
            self.run_beakerlib_command(['rlPass', 'PASS %s' % desc])
        else:
            self.run_beakerlib_command(['rlLogError', call.excinfo.exconly()])
            short_repr = str(call.excinfo.getrepr(style='short'))
            self.run_beakerlib_command(['rlLogInfo', short_repr])

            # Give super-detailed traceback for DEBUG=1
            long_repr = str(call.excinfo.getrepr(
                showlocals=True, funcargs=True))
            self.run_beakerlib_command(['rlLogDebug', long_repr])

            if call.excinfo.errisinstance(pytest.skip.Exception):
                self.run_beakerlib_command(['rlPass', 'SKIP %s' % desc])
            else:
                self.run_beakerlib_command(['rlFail', 'FAIL %s' % desc])

    def pytest_unconfigure(self, config):
        """Clean up and exit"""
        self.set_current_item(None)
        self.process.end()
