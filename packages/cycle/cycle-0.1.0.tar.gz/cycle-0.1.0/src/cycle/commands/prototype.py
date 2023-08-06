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
import argparse
from datetime import datetime
import os
import shlex
# import third party libs
# import local libs
from cycle.baseshell import BaseShell
from cycle.generators.generic import GenericGenerator
from cycle.utils import format_json, load_resource_json


class PrototypeCmd(BaseShell):
    """Cycle Prototype Command"""

    def __init__(self, mode_onecmd=False):
        BaseShell.__init__(self, mode_onecmd, group='cycle.commands.registered_commands')
     
    def do_generate(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument("project_name", help="Project name")
        parser.add_argument("--prototype", "-p",
                            default="cycle.prototypes.python.base",
                            help="Prototype to use for new project")
        args = parser.parse_args(shlex.split(args))
        metadata = {}
        metadata['project_name'] = args.project_name
        metadata['prototype'] = args.prototype
        metadata['author_username'] = os.environ['USER']
        wizard = load_resource_json("data/prototypes/%s/wizard.json" % args.prototype)
          
        print
        print "Cycle prototype generator"
        print "The following questions helps to get all required metadata."
        print "The prototype generator recommends to use Semantic Versioning (semver.org)"
        print
          
        for step in wizard:
            answer = raw_input(step['q'] + ' [' + step['default'] % metadata + '] \n>>  ').strip()
            if answer == '':
                answer = step['default'] % metadata
            metadata[step['key']] = answer
  
        print format_json(metadata)
        commit = None
        while not commit in ('n', 'N', 'y', 'Y'):
            commit = raw_input("Generate the project with this metadata: Continue? [n/y]").strip()
            if commit in ('y', 'Y'):
                print "Generating module"
                metadata['datetime_created'] = datetime.now()
                GenericGenerator.generate(metadata['project_name'],metadata,
                                          metadata['prototype'])
            elif commit in ('n', 'N'):
                print "Aborted by user. Exiting"
            else:
                pass


def main(args):
    PrototypeCmd().onecmd(args)
