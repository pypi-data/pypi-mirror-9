#!/usr/bin/env python3

# Copyright 2012-2014 Louis Paternault
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

"""Test de la génération de jeux."""

import unittest

from jouets import dobble

# pylint: disable=too-many-public-methods
class TestBuild(unittest.TestCase):
    """Test de la génération de jeux."""

    def test_exception(self):
        """Génération incorrecte"""
        for taille in [4, 6, 100]:
            self.assertRaises(
                dobble.TailleNonGeree,
                dobble.genere_jeu, taille
                )

    def test_regulier(self):
        """Génération correcte."""
        for taille in [1, 2, 3, 5, 7, 11]:
            self.assertTrue(dobble.genere_jeu(taille).regulier)

if __name__ == '__main__':
    unittest.main()
