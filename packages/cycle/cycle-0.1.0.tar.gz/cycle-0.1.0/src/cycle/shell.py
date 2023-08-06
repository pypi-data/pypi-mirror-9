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
import sys
# import third party libs
# import local libs
from cycle import meta
from cycle.baseshell import BaseShell


class CycleShell(BaseShell):
    """VirtualDC Cli"""

    def __init__(self, mode_onecmd=False):
        BaseShell.__init__(self, mode_onecmd, group='cycle.registered_commands')
        self.intro = ('Cycle Shell v%s For list of commands type help or ?\n'
                  % (meta.__version__))
        self.prompt = 'cycle >> '


def main():
    CycleShell(mode_onecmd=True).onecmd(' '.join(sys.argv[1:]))


if __name__ == '__main__':
    main()
