# Copyright (C) 2014-2015 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import os.path
import pkg_resources


def resource_path(*path):
    return pkg_resources.resource_filename('vmcloak', os.path.join(*path))


def load_resource(*path):
    return pkg_resources.resource_string('vmcloak', os.path.join(*path))


def list_resources(*path):
    return pkg_resources.resource_listdir('vmcloak', os.path.join(*path))
