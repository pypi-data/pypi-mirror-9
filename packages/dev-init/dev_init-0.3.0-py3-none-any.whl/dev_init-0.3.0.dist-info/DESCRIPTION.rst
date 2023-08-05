dev-init
========

Automated development environment initialization

Requirements
------------

- Python 2 or 3 (tested in Python 2.7 and 3.4)

Usage
-----

For help on a specific command, run `dev-init COMMAND --help`::

    usage: dev-init [-h] [--version] {list,new,remove,show,start} ...

    Automated development environment initialization

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

    commands:
      {list,new,remove,show,start}
        list                list all the available environment types
        new                 define a new environment type
        remove              remove an environment type from the configuration file
        show                show the commands performed for a specific environment
        start               start a new environment


