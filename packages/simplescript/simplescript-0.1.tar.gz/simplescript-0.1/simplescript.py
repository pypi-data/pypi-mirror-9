# Copyright 2015 Mark Haines
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


import inspect
from sys import stdin, stdout
from argparse import FileType, ArgumentParser

__version__ = "0.1"


def add_arguments(parser, function):
    spec = inspect.getargspec(function)
    optional = zip(spec.args[-len(spec.defaults):], spec.defaults)
    required = spec.args[:-len(spec.defaults)]
    for arg in required:
        parser.add_argument(arg.replace("_", "-"))
    for arg, default in optional:
        arg = arg.replace("_", "-")
        if default is True:
            parser.add_argument(
                "--no-" + arg,
                action="store_false",
                dest=arg.replace("-", "_"),
                default=True
            )
        elif default is False:
            parser.add_argument(
                "--" + arg,
                action="store_true",
                default=False,
            )
        elif default is stdin:
            parser.add_argument(
                "--" + arg,
                type=FileType('r'),
                default=stdin,
            )
        elif default is stdout:
            parser.add_argument(
                "--" + arg,
                type=FileType('w'),
                default=stdout,
            )
        elif type(default) is FileType:
            parser.add_argument(
                "--" + arg,
                type=default,
            )
        elif default == []:
            parser.add_argument(
                "--" + arg,
                action="append"
            )
        else:
            parser.add_argument(
                "--" + arg,
                type=type(default),
                default=default,
            )


def simplescript(function):
    if function.__module__ == "__main__":
        parser = ArgumentParser(
            description=inspect.getdoc(function)
        )
        add_arguments(parser, function)
        args = parser.parse_args()
        function(**args.__dict__)
    return function
