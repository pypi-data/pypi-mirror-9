'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from __future__ import absolute_import


import subprocess
import logging
import os


from ... import domain


class VersionControlSystem(domain.MetricSource):
    # pylint: disable=abstract-class-not-used
    ''' Abstract base class for version control systems such as Subversion and
        Git. '''

    metric_source_name = 'Version control system'

    def __init__(self, username=None, password=None, url=None,
                 run_shell_command=subprocess.check_output):
        self._username = username
        self._password = password
        self._shell_command = run_shell_command
        super(VersionControlSystem, self).__init__(url=url)

    def last_changed_date(self, url):
        ''' Return the date when the url was last changed. '''
        raise NotImplementedError  # pragma: no cover

    def latest_tagged_product_version(self, path):
        # pylint: disable=unused-arguments
        ''' Return the latest version as tagged in the VCS. '''
        return ''

    def branches(self, path):
        # pylint: disable=unused-arguments
        ''' Return a list of branch names for the specified path. '''
        raise NotImplementedError  # pragma: no cover

    def unmerged_branches(self, path):
        # pylint: disable=unused-arguments
        ''' Return a dictionary of branch names and number of unmerged
            revisions for each branch that has any unmerged revisions. '''
        raise NotImplementedError  # pragma: no cover

    def normalize_path(self, path):
        ''' Return a normalized version of the path. '''
        return path

    def _run_shell_command(self, shell_command, folder=None,
                           log_level=logging.WARNING):
        ''' Invoke a shell and run the command. If a folder is specified,
            run the command in that folder. '''
        original_working_dir = os.getcwd()
        if folder:
            os.chdir(folder)
        try:
            return self._shell_command(shell_command)
        except subprocess.CalledProcessError, reason:
            # No need to include the shell command in the log, because the
            # reason contains the shell command.
            logging.log(log_level, 'Shell command failed: %s', reason)
            if log_level > logging.WARNING:
                raise
        finally:
            os.chdir(original_working_dir)
