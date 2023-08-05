# Topydo - A todo.txt client written in Python.
# Copyright (C) 2014 Bram Schoenmakers <me@bramschoenmakers.nl>
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

from topydo.lib.Command import Command

class ListProjectCommand(Command):
    def __init__(self, p_args, p_todolist,
                 p_out=lambda a: None,
                 p_err=lambda a: None,
                 p_prompt=lambda a: None):
        super(ListProjectCommand, self).__init__(
            p_args, p_todolist, p_out, p_err, p_prompt)

    def execute(self):
        if not super(ListProjectCommand, self).execute():
            return False

        for project in sorted(self.todolist.projects(), key=str.lower):
            self.out(project)

    def usage(self):
        return """Synopsis: lscon"""

    def help(self):
        return """Lists all projects in the todo list."""
