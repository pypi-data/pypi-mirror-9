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

"""Tests de fonctions internes"""

import unittest
import textwrap

from jouets import dobble

# pylint: disable=too-many-public-methods
class TestCore(unittest.TestCase):
    """Test de fonctions internes"""

    def test_iterateurs(self):
        """Itérateurs"""
        ensemble_cartes = {
            dobble.CarteDobble(['1', '2', '3']),
            dobble.CarteDobble(['1', 'a', 'b']),
            dobble.CarteDobble(['1', 'x', 'y']),
            dobble.CarteDobble(['2', 'a', 'x']),
            dobble.CarteDobble(['2', 'b', 'y']),
            dobble.CarteDobble(['3', 'a', 'y']),
            dobble.CarteDobble(['3', 'b', 'x']),
            }
        jeu = dobble.JeuDobble(ensemble_cartes)

        for carte in jeu:
            self.assertIn(carte, ensemble_cartes)

        for symbol in jeu.cartes[0]:
            self.assertIn(symbol, ['1', '2', '3', 'a', 'b', 'x', 'y'])

    def test_str(self):
        """Conversion en chaînes de caractères"""
        jeu = dobble.JeuDobble({
            dobble.CarteDobble(['1', '2', '3']),
            dobble.CarteDobble(['1', 'a', 'b']),
            dobble.CarteDobble(['1', 'x', 'y']),
            dobble.CarteDobble(['2', 'a', 'x']),
            dobble.CarteDobble(['2', 'b', 'y']),
            dobble.CarteDobble(['3', 'a', 'y']),
            dobble.CarteDobble(['3', 'b', 'x']),
            })

        self.assertEqual(
            str(dobble.CarteDobble(['1', 'a', 'bc'])),
            "1 a bc"
            )

        self.assertEqual(
            str(jeu),
            textwrap.dedent("""\
                1 2 3
                1 a b
                1 x y
                2 a x
                2 b y
                3 a y
                3 b x""")
            )

    def test_equal(self):
        """Test d'égalité"""
        self.assertNotEqual(
            dobble.CarteDobble(['1', '2']),
            dobble.CarteDobble(['12'])
            )
        self.assertEqual(
            dobble.CarteDobble(['1', '2']),
            dobble.CarteDobble(['2', '1'])
            )

        self.assertNotEqual(
            dobble.JeuDobble({
                dobble.CarteDobble(['1', '2']),
                dobble.CarteDobble(['2', '3'])
                }),
            dobble.JeuDobble({
                dobble.CarteDobble(['1', '2']),
                dobble.CarteDobble(['23'])
                })
            )
        self.assertEqual(
            dobble.JeuDobble({
                dobble.CarteDobble(['1', '2']),
                dobble.CarteDobble(['2', '3'])
                }),
            dobble.JeuDobble({
                dobble.CarteDobble(['3', '2']),
                dobble.CarteDobble(['2', '1'])
                })
            )

if __name__ == '__main__':
    unittest.main()
