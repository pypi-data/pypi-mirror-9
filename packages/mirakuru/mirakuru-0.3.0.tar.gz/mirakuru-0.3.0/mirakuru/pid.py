# Copyright (C) 2014 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of mirakuru.

# mirakuru is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mirakuru is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with mirakuru.  If not, see <http://www.gnu.org/licenses/>.
"""Pid executor definition."""

import os.path
from mirakuru.base import StartCheckExecutor


class PidExecutor(StartCheckExecutor):

    """
    File existence checking process executor.

    Used to start processes that create pid files (or any other for that
    matter). Starts the given process and waits for the given file to be
    created.
    """

    def __init__(self, command, filename,
                 shell=False, timeout=None, sleep=0.1):
        """
        Initialize the PidExecutor executor.

        If the filename is empty, a ValueError is thrown.

        :param str command: the command to run which is to create a file
        :param str filename: the file which is to exist
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for the process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop conditions
        :raises: ValueError
        """
        if not filename:
            raise ValueError("filename cannot be empty")
        super(PidExecutor, self).__init__(
            command, shell=shell, timeout=timeout, sleep=sleep
        )
        self.filename = filename
        """the name of the file which the process is to create."""

    def pre_start_check(self):
        """
        Check if the specified file has been created.

        .. note::

            The process will be considered started when it will have created
            the specified file as defined in the initializer.
        """
        return os.path.isfile(self.filename)

    def after_start_check(self):
        """
        Check if the process has created the specified file.

        .. note::

            The process will be considered started when it will have created
            the specified file as defined in the initializer.
        """
        return self.pre_start_check()  # we can reuse logic from `pre_start()`
