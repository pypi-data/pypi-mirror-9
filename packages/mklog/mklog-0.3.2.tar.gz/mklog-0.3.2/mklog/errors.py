# Copyright Louis Paternault 2011-2015
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Errors and exceptions"""

class MklogError(Exception):
    """Generic error for mklog"""
    pass

class ExecutionError(MklogError):
    """Error while running user command"""
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return "Error when running '{}'.".format(" ".join(self.message))
