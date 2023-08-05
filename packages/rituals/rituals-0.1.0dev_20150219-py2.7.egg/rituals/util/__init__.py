# -*- coding: utf-8 -*-
""" rituals.util – Helper modules.
"""
# Copyright ⓒ  2015 Jürgen Hermann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# The full LICENSE file and source are available at
#    https://github.com/jhermann/rituals

import os


def search_file_upwards(name, base=None):
    """ Search for a file named `name` from cwd or given directory to root.
        Return None if nothing's found.
    """
    base = base or os.getcwd()
    while base != os.path.dirname(base):
        if os.path.exists(os.path.join(base, name)):
            return base
        base = os.path.dirname(base)

    return None

