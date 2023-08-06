# Copyright (c) 2003-2014 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
"""logilab.devtools packaging information"""

modname = 'devtools'
distname = 'logilab-devtools'
numversion = (0, 24, 0)
version = '.'.join([str(num) for num in numversion])

license = 'GPL'
author = "Logilab"
author_email = "contact@logilab.fr"

description = "set of development tools used at Logilab"
web = "http://www.logilab.org/project/logilab-devtools"
mailinglist = "mailto://python-projects@lists.logilab.org"

subpackage_of = 'logilab'

scripts = [
    'bin/lsprofcalltree',
    'bin/grmerge',
    'bin/gmmerge',
    'bin/tagsmerge',
    'bin/jobtest',
    'bin/pygrep',
    ]

packages = ['hgext.jpl']

install_requires = ['logilab-common']
