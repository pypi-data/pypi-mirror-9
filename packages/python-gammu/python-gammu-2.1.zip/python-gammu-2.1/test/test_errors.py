# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This file is part of Gammu <http://wammu.eu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import unittest
import gammu.exception


def error_function():
    raise gammu.exception.ERR_WRONGCRC()


class ErrorTest(unittest.TestCase):
    def test_catching(self):
        self.assertRaises(
            gammu.exception.GSMError,
            error_function,
        )
