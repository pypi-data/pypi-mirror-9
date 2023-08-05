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

from topydo.lib.Command import Command, InvalidCommandArgument
from topydo.lib.TodoListBase import InvalidTodoException
from topydo.lib.PrettyPrinter import pretty_print

class TagCommand(Command):
    def __init__(self, p_args, p_todolist,
                 p_out=lambda a: None,
                 p_err=lambda a: None,
                 p_prompt=lambda a: None):
        super(TagCommand, self).__init__(
            p_args, p_todolist, p_out, p_err, p_prompt)

        self.force = False
        self.force_add = False
        self.todo = None
        self.tag = None
        self.value = None
        self.values = []
        self.current_values = []

    def _process_flags(self):
        flags, args = self.getopt("af")
        for flag, _ in flags:
            if flag == "-a":
                self.force_add = True
            elif flag == "-f":
                self.force = True

        self.args = args

    def _process_args(self):
        self._process_flags()

        try:
            self.todo = self.todolist.todo(self.argument(0))
            self.tag = self.argument(1)
            self.current_values = self.todo.tag_values(self.tag)
        except (InvalidCommandArgument, InvalidTodoException):
            self.error("Invalid todo number.")

        try:
            self.value = self.argument(2)
        except InvalidCommandArgument:
            self.value = ""

    def _print(self):
        self.out(pretty_print(self.todo, [self.todolist.pp_number()]))

    def _choose(self):
        """
        Returns the chosen number of the tag value to process (or "all")
        """
        answer = "all"

        if not self.force:
            for i, value in enumerate(self.current_values):
                self.out("{:>2d}. {}".format(i + 1, value))

            answer = self.prompt(
                'Which value to remove? Enter number or "all": ')

        if answer != "all":
            try:
                answer = int(answer) - 1

                if answer < 0 or answer >= len(self.current_values):
                    answer = None
            except ValueError:
                answer = None

        return answer

    def _set_helper(self, p_old_value=""):
        old_src = self.todo.source()
        self.todo.set_tag(self.tag, self.value, self.force_add, p_old_value)

        if old_src != self.todo.source():
            self.todolist.set_dirty()

    def _set(self):
        if len(self.current_values) > 1:
            answer = self._choose()

            if answer == "all":
                for value in self.current_values:
                    self._set_helper(value)
            elif answer != None and self.value != self.current_values[answer]:
                self._set_helper(self.current_values[answer])

        else:
            self._set_helper()

        self._print()

    def execute(self):
        if not super(TagCommand, self).execute():
            return False

        self._process_args()

        if self.todo and self.tag:
            self._set()

    def usage(self):
        return """Synopsis: tag [-a] [-f] <NUMBER> <tag> [<value>]"""

    def help(self):
        return """\
Sets the given tag to the given todo number with the given value. If the value
is omitted, the tag is removed from the todo item.

-a : Do not change the current value of the tag if it exists, but add a new
     value.
-f : Force setting/removing all values of the tag. Prevents interaction with the
     user.
"""
