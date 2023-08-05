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


CONFIG = os.path.join(os.path.expanduser("~"), ".dev-init")


def init_parser():
    """ Initialize the arguments parser. """
    parser = argparse.ArgumentParser(
        description="Automated development environment initialization")

    # List group
    group_list = parser.add_argument_group()
    group_list.add_argument("-l", "--list", action="store_true",
        help="list all the available environment types")

    # Actions group
    group_actions = parser.add_mutually_exclusive_group()

    group_actions.add_argument("-n", "--new", metavar="env",
        help="define a new environment type")

    group_actions.add_argument("-r", "--remove", metavar="env",
        help="remove an environment type from the configuration file")

    group_actions.add_argument("-s", "--show", metavar="env",
        help="show the commands performed for a specific environemnt")

    # Default init group
    group_init = parser.add_argument_group()
    group_init.add_argument("init_env", metavar="environment", nargs="?",
        help="initialize the specified environment in current directory")

    return parser

def init_env(environment):
    """ Initialize a new environment in current working directory. """
    parser = read_config()

    if environment not in parser.sections():
        print("Unknown environment type '%s'" % environment)
        return

    commands = parser.get(environment, "cmd").split("\n")

    for cmd in commands:
        proc = subprocess.Popen(cmd , cwd=os.getcwd(), shell=True)
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
    parser = read_config()

    if not parser.remove_section(environment):
        print("Unknown environment type '%s'" % environment)
        return

    write_config(parser)

    print("Removed environment '%s'" % environment)

def show_env(environment):
    """ Show the commands for a given environment. """
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
    if parsed.init_env:
        init_env(parsed.init_env)

    elif parsed.list:
        list_env()

    elif parsed.new:
        new_env(parsed.new)

    elif parsed.remove:
        remove_env(parsed.remove)

    elif parsed.show:
        show_env(parsed.show)

def main():
    parser = init_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        # No argument provided
        parser.print_help()

    parse_action(args)
