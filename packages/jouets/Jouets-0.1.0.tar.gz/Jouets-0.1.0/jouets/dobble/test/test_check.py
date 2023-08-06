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

"""Test de la vérification de jeux de dobble."""

import unittest
import io

from jouets import dobble

IRREGULIER = """\
        1 2 3
        1 a b
        1 x y
        2 a x
        2 b y
        3 a y
        """

# pylint: disable=too-many-public-methods
class TestAnalyseFichier(unittest.TestCase):
    """Test de lecture et analyse de fichiers."""

    def test_fichier_vide(self):
        """Lecture de fichier vide."""
        self.assertEqual(
            dobble.analyse_fichier(io.StringIO('')),
            dobble.JeuDobble()
            )

    def test_fichier_valide(self):
        """Lecture de jeux valides."""
        self.assertEqual(
            dobble.analyse_fichier(io.StringIO("""\
                1 2 a z
                a b 23 t

                t 2
                """)),
            dobble.JeuDobble({
                dobble.CarteDobble(['1', '2', 'a', 'z']),
                dobble.CarteDobble(['a', 'b', '23', 't']),
                dobble.CarteDobble(['t', '2']),
                })
            )

class TestUtils(unittest.TestCase):
    """Tests de fonctions intermédiaires."""

    def test_resume(self):
        """Test du résumé."""
        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 b
                1 a
                1 2
                2 a b
                """))
        self.assertDictEqual(
            jeu.frequences_symboles,
            {
                '1': 3,
                'a': 2,
                'b': 2,
                '2': 2,
            }
            )

    def test_ensemble(self):
        """Test des fonctions ensemblistes."""
        jeu = dobble.analyse_fichier(io.StringIO(IRREGULIER))
        self.assertFalse(jeu.regulier)

        jeu.cartes.append(dobble.CarteDobble(['3', 'b', 'x']))
        self.assertTrue(jeu.regulier)

        jeu.cartes[0].symboles.append('*')
        self.assertFalse(jeu.regulier)



class TestVerification(unittest.TestCase):
    """Test de vérification de jeux"""

    def test_valide(self):
        """Validité"""
        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 2 3
                1 2 a
                1 3 b
                """))
        self.assertFalse(jeu.valide)

        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 2
                1
                """))
        self.assertTrue(jeu.valide)

        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 1
                1 2
                """))
        self.assertFalse(jeu.valide)


    def test_regulier(self):
        """Régularité"""
        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 2 3
                1 a b
                1 x y
                2 a x
                2 b y
                3 a y
                3 b x
                """))
        self.assertTrue(jeu.regulier)

        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 2
                1 3
                2 3
                1 3
                """))
        self.assertFalse(jeu.valide)
        self.assertFalse(jeu.regulier)

    def test_trivial(self):
        """Trivialité"""
        jeu = dobble.analyse_fichier(io.StringIO("""\
                1 2 3
                1 a b
                1 x y
                2 a x
                2 b y
                3 a y
                3 b x
                """))
        self.assertFalse(jeu.trivial)

        jeu = dobble.analyse_fichier(io.StringIO("""\
                1
                1
                1
                1
                1
                """))
        self.assertTrue(jeu.valide)
        self.assertTrue(jeu.trivial)
        self.assertTrue(jeu.regulier)

        jeu = dobble.analyse_fichier(io.StringIO("""\
                1
                """))
        self.assertTrue(jeu.valide)
        self.assertTrue(jeu.trivial)
        self.assertTrue(jeu.regulier)

if __name__ == '__main__':
    unittest.main()
