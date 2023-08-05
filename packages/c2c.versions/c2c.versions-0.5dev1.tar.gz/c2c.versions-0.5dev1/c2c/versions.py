# -*- coding: utf-8 -*-

# Copyright (c) 2011-2014, Camptocamp SA
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.


import sys
import yaml
from distutils.version import LooseVersion

try:
    from subprocess import check_output
except ImportError:  # pragma: nocover
    from subprocess import Popen, PIPE

    def check_output(cmd, cwd=None, stdin=None, stderr=None, shell=False):  # noqa
        """Backwards compatible check_output"""
        p = Popen(cmd, cwd=cwd, stdin=stdin, stderr=stderr, shell=shell, stdout=PIPE)
        out, err = p.communicate()
        return out


def main():
    if len(sys.argv) != 3:  # pragma: nocover
        print("Usage: {cmd} <config file> <section>")

    with open(sys.argv[1]) as config_file:
        config = yaml.load(config_file)

        default_cmd = config['default_cmd']
        section = config[sys.argv[2]]
        error = 0

        for package in section.keys():
            version_object = section[package]
            if not isinstance(version_object, dict):
                cmd = default_cmd
                version_str = str(version_object)
                operation = '>='
            else:
                cmd = version_object.get('cmd', default_cmd)
                version_str = str(version_object.get('version', '0'))
                operation = version_object.get('operation', '>=')
                if version_object.get('can_be_virtual', False):
                    output = check_output(
                        ['/usr/bin/apt-cache', 'showpkg', package]
                    ).decode('utf-8')
                    packages = [package]
                    in_reverse_provides = False
                    for line in output.split('\n'):
                        l = line.strip()
                        if len(l) > 0 and l[-1] == ':':
                            in_reverse_provides = l == 'Reverse Provides:'
                        elif in_reverse_provides and len(line) > 0:
                            packages.append(line.split()[0])
                    package = ' '.join(packages)

            version = LooseVersion(version_str)
            try:
                current_version_str = check_output(
                    cmd.format(package=package), shell=True
                ).decode('utf-8').split('\n')[0].strip()
            except:  # pragma: nocover
                print(
                    "{package} doesn't seam to be installed "
                    "(required version: {version}).".format(
                        package=package, version=version_str
                    )
                )
                error = 1
                continue
            if len(current_version_str) == 0:  # pragma: nocover
                print(
                    "{package} doesn't seam to be installed "
                    "(required version: {version}).".format(
                        package=package, version=version_str
                    )
                )
                error = 1
                continue

            current_version = LooseVersion(current_version_str)

            if operation == '==':
                if not version == current_version:
                    print(
                        "{package} doesn't have the right version "
                        "({current_version} <> {version})".format(
                            package=package,
                            current_version=current_version_str,
                            version=version_str
                        )
                    )
                    error = 1
            elif operation == '<':
                if not current_version < version:
                    print(
                        "{package} doesn't have the right version "
                        "({current_version} >= {version})".format(
                            package=package,
                            current_version=current_version_str,
                            version=version_str
                        )
                    )
                    error = 1
            elif operation == '>':
                if not current_version > version:
                    print(
                        "{package} doesn't have the right version "
                        "({current_version} <= {version})".format(
                            package=package,
                            current_version=current_version_str,
                            version=version_str
                        )
                    )
                    error = 1
            elif operation == '<=':
                if not current_version < version:
                    print(
                        "{package} doesn't have the right version "
                        "({current_version} > {version})".format(
                            package=package,
                            current_version=current_version_str,
                            version=version_str
                        )
                    )
                    error = 1
            elif operation == '>=':
                if not current_version >= version:
                    print(
                        "{package} doesn't have the right version "
                        "({current_version} < {version})".format(
                            package=package,
                            current_version=current_version_str,
                            version=version_str
                        )
                    )
                    error = 1
            else:  # pragma: nocover
                print("Unknown operation: %s" % operation)
                error = 1

        exit(error)
