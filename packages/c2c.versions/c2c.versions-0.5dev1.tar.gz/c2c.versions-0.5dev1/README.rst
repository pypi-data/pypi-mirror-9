c2c.versions
============

Command to tests program version.

Example of use:

Config file:

code:: yaml

    default_cmd: dpkg -l {package} | grep ^ii | awk '{{print $3}}'

    main:
        python: # use python version
            cmd: /usr/bin/python --version 2>&1 | awk '{{print $2}}'
            version: 2.7 
        python3: # use package verion
            version: 3.3

Command:

``c2c.versions config.yaml main``

This example tests that we have at least the version 2.7 of python 2
and the version 3.3 of python 3.
