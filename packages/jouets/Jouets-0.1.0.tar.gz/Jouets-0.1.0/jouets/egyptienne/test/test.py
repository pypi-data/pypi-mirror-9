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

"""Test de egyptienne.py"""

#pylint: disable=invalid-name

import unittest

from jouets.egyptienne import egyptienne, irreductible, pgcd

# pylint: disable=too-many-public-methods
class TestFonctions(unittest.TestCase):
    """Vérifications des fonctions"""

    def test_pgcd(self):
        """Vérification de la fonction pgcd()"""
        temoin = [
            [2, 2, 2],
            [3, 5, 1],
            [15, 35, 5],
            [150, 60, 30],
            ]
        for (a, b, resultat) in temoin:
            self.assertEqual(
                resultat,
                pgcd(a, b),
            )

    def test_irreductible(self):
        """Vérification de la fonction irreductible()"""
        temoin = [
            [2, 3, (2, 3)],
            [10, 15, (2, 3)],
            ]
        for (a, b, resultat) in temoin:
            self.assertTupleEqual(
                resultat,
                irreductible(a, b),
            )

    def test_egyptienne(self):
        """Vérification de la fonction egyptienne()"""
        temoin = [
            [1, 3, [3]],
            [2, 3, [2, 6]],
            [9, 20, [3, 9, 180]],
            [4, 3, [1, 3]],
            ]
        for (a, b, resultat) in temoin:
            self.assertListEqual(
                resultat,
                egyptienne(a, b),
            )

if __name__ == '__main__':
    unittest.main()
