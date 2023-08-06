# Copyright 2015: Boris Pavlovic
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


def parse_args(argv):

    args = {"positional": []}

    i = 0
    args_are_positional = True
    current_arg_name = None
    while i < len(argv):
        if args_are_positional:
            if argv[i].startswith("--"):
                args_are_positional = False
            else:
                args["positional"].append(argv[i])
                i += 1
                continue

        if argv[i].startswith("--"):
            current_arg_name = argv[i][2:]
            args[current_arg_name] = []
        else:
            args[current_arg_name].append(argv[i])
        i += 1

    return args
