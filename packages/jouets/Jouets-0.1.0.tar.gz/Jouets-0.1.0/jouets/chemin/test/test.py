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

"""Test de chemin.py"""

import unittest

from jouets.chemin import Resolution

TEMOIN = [
    [1, 3, 10, 2, 7, 20, 1, 30, 57],
    [1, 3, 10, 2, 7, 20, 1, 57, 27],
    [1, 30, 57, 2, 7, 20, 1, 3, 10],
    [1, 57, 27, 2, 7, 20, 1, 3, 10],
    ]

# pylint: disable=too-many-public-methods
class TestOptimales(unittest.TestCase):
    """Recherche et vérifie les solutions optimales"""

    def test(self):
        """Vérifie les solutions optimales"""
        solutions = Resolution()
        solutions.recherche()

        self.assertCountEqual(
            [solution.array.array for solution in solutions.top],
            TEMOIN,
        )

if __name__ == '__main__':
    unittest.main()
