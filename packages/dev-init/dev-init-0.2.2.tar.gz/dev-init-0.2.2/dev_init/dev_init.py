# -*- coding: utf-8 -*-
#
# dev-init - automated development environment initialization
# https://github.com/rmed/dev-init
#
# Copyright (C) 2014  Rafael Medina García <rafamedgar@gmail.com>
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

from __future__ import absolute_import
import argparse
import os
import subprocess
import sys
# Python 2 and 3 compatibility
try:
    from configparser import ConfigParser
except:
    from ConfigParser import ConfigParser
if sys.version[0] == "3": raw_input=input


__version__ = "0.2.2"

CONFIG = os.path.join(os.path.expanduser("~"), ".dev-init")


def init_parser():
    """ Initialize the arguments parser. """
    parser = argparse.ArgumentParser(
        description="Automated development environment initialization")

    parser.add_argument('--version', action='version',
        version='%(prog)s ' + __version__)

    parser.add_argument("-l", "--list", action="store_true",
        help="list all the available environment types")

    # Actions group
    group_actions = parser.add_mutually_exclusive_group()

    group_actions.add_argument("-n", "--new", action="store_true",
        help="define a new environment type")

    group_actions.add_argument("-r", "--remove", action="store_true",
        help="remove an environment type from the configuration file")

    group_actions.add_argument("-s", "--show", action="store_true",
        help="show the commands performed for a specific environemnt")

    group_actions.add_argument("-p", "--path", metavar="path",
        help="path in which to initialize the environment")

    parser.add_argument("env", metavar="environment", nargs="?",
        help="environment name to initialize/create/remove/show")

    return parser

def init_env(environment, path):
    """ Initialize a new environment in specified directory.

        If path does not exist, will try to create the directory structure
        recursively.

        If the path is not provided, will use current working directory.
    """
    parser = read_config()

    if environment not in parser.sections():
        print("Unknown environment type '%s'" % environment)
        return

    if path and not os.path.isdir(path):
        try:
            os.makedirs(path)
        except os.error:
            print("Could not create directory structure")
            return

    init_path = path if path else os.getcwd()

    commands = parser.get(environment, "cmd").split("\n")

    print("Working in directory: " + init_path)

    for cmd in commands:
        proc = subprocess.Popen(cmd , cwd=init_path, shell=True)
        proc.wait()

    print("Initialized '%s' environment" % environment)

def list_env():
    """ List all the available environments in the configuration. """
    parser = read_config()

    for env in parser.sections():
        print(env)

def new_env(environment):
    """ Create a new environment in the configuration and ask the
        user for the commands for this specific environment.
    """
    if not environment:
        print("You need to supply an environment name")
        return

    parser = read_config()

    if environment in parser.sections():
        print("Environment '%s' already exists" % environment)
        return

    print("Please introduce (in order) the commands for '%s'\n" % environment)
    print("Press RETURN to end command and RETURN with empty line to finish\n")

    commands = []
    cmd = ""

    while True:
        try:
            cmd = raw_input("> ")

            if not cmd:
                break

            commands.append(cmd)

        except KeyboardInterrupt:
            return

    parser.add_section(environment)
    parser.set(environment, "cmd", "\n".join(commands))

    write_config(parser)

    print("Added environment '%s'" % environment)

def remove_env(environment):
    """ Remove an environment from the configuration. """
    if not environment:
        print("You need to supply an environment name")
        return

    parser = read_config()

    if not parser.remove_section(environment):
        print("Unknown environment type '%s'" % environment)
        return

    write_config(parser)

    print("Removed environment '%s'" % environment)

def show_env(environment):
    """ Show the commands for a given environment. """
    if not environment:
        print("You need to supply an environment name")
        return

    parser = read_config()

    try:
        commands = parser.get(environment, "cmd").split("\n")

    except KeyError:
        print("Unknown environment type '%s'" % environment)
        return

    print("Environment: %s\n" % environment)

    for cmd in commands:
        print(cmd)

def read_config():
    """ Read the configuration file and parse the different environments.

        Returns: ConfigParser object
    """
    if not os.path.isfile(CONFIG):
        with open(CONFIG, "w"):
            pass

    parser = ConfigParser()
    parser.read(CONFIG)

    return parser

def write_config(parser):
    """ Write back new configuration to file. """
    with open(CONFIG, "w") as config_file:
        parser.write(config_file)

def parse_action(parsed):
    """ Parse the action to execute. """
    if parsed.list:
        list_env()

    elif parsed.new:
        new_env(parsed.env)

    elif parsed.remove:
        remove_env(parsed.env)

    elif parsed.show:
        show_env(parsed.env)

    elif parsed.env:
        init_env(parsed.env, parsed.path)

def main():
    parser = init_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # No argument provided
        parser.print_help()

    parse_action(args)
