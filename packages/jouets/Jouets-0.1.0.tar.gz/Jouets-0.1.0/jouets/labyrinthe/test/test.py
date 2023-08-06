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

"""Test de labyrinthe.py"""

import unittest

from jouets.labyrinthe.shapes.turtle.square import \
        Labyrinthe as LabyrintheCarre
from jouets.labyrinthe.shapes.turtle.triangle import \
        Labyrinthe as LabyrintheTriangle
from jouets.labyrinthe.shapes.turtle.random1 import \
        Labyrinthe as LabyrintheRandom1

# pylint: disable=too-many-public-methods
class TestPremiers(unittest.TestCase):
    """Vérification de la liste des nombres générés"""

    def test_carre(self):
        """Génération et vérification d'un labyrinthe à base carrée"""
        lab = LabyrintheCarre(taille=10, affiche=False)
        lab.construit()
        self.assertListEqual(
            lab.invalides(),
            [],
        )

    def test_triangle(self):
        """Génération et vérification d'un labyrinthe à base triangulaire"""
        lab = LabyrintheTriangle(taille=10, affiche=False)
        lab.construit()
        self.assertListEqual(
            lab.invalides(),
            [],
        )

    def test_random1(self):
        """Génération et vérification d'un labyrinthe à base aléatoire"""
        lab = LabyrintheRandom1(taille=10, affiche=False)
        lab.construit()
        self.assertListEqual(
            lab.invalides(),
            [],
        )

if __name__ == '__main__':
    unittest.main()
