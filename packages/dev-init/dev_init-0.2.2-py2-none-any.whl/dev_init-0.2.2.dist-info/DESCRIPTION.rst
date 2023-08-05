dev-init
========

Automated development environment initialization

Requirements
------------

- Python 2 or 3 (tested in Python 2.7 and 3.4)

Usage
-----

::

    usage: dev_init [-h] [--version] [-l] [-n | -r | -s | -p path]
                       [environment]

    Automated development environment initialization

    positional arguments:
      environment           environment name to initialize/create/remove/show

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -l, --list            list all the available environment types
      -n, --new             define a new environment type
      -r, --remove          remove an environment type from the configuration file
      -s, --show            show the commands performed for a specific environemnt
      -p path, --path path  path in which to initialize the environment


