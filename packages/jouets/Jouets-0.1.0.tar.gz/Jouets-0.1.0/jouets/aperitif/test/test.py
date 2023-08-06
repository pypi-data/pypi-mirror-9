#!/usr/bin/env python3

# Copyright 2014 Louis Paternault
#
# This file is part of Jouets.
#
# Jouets is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jouets is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jouets.  If not, see <http://www.gnu.org/licenses/>.

"""Test de aperitif.py"""

import unittest

from jouets.aperitif import aperitif

TEMOINS = [
    (
        # http://xkcd.com/287/
        [215, 275, 335, 355, 420, 580],
        1505,
        [[1, 0, 0, 2, 0, 1], [7, 0, 0, 0, 0, 0]],
    ),
    (
        [7, 8, 9],
        30,
        [[2, 2, 0], [3, 0, 1]],
    ),
    ]
# pylint: disable=too-many-public-methods
class TestPremiers(unittest.TestCase):
    """Vérification de solutions"""

    def test(self):
        """Quelques solutions"""
        for (prix, total, solutions) in TEMOINS:
            self.assertCountEqual(
                solutions,
                aperitif(total, prix),
            )

if __name__ == '__main__':
    unittest.main()
