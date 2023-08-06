# Copyright 2015 refnode
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# import std libs
import cmd
import pkg_resources
# import third party libs
# import local libs


class BaseShell(cmd.Cmd):

    def __init__(self, mode_onecmd=False, group=None):
        cmd.Cmd.__init__(self)
        self.mode_onecmd = mode_onecmd
        if group:
            registered_commands = list(pkg_resources.iter_entry_points(group=group))
        for c in registered_commands:
            main = c.load()
            setattr(self, 'do_' + c.name, main)

    def get_names(self):
        return dir(self)
    
    def do_hist(self, args):
        print self._hist

    def do_exit(self, args):
        return -1

    def do_EOF(self, args):
        print '\n'
        return self.do_exit(args)

    def preloop(self):
        cmd.Cmd.preloop(self)
        self._hist = []
        self._locals = {}
        self._globals = {}

    def precmd(self, line):
        self._hist += [line.strip()]
        return line
    
    def _registered_commands(self, group='cycle.registered_commands'):
        return list(pkg_resources.iter_entry_points(group=group))