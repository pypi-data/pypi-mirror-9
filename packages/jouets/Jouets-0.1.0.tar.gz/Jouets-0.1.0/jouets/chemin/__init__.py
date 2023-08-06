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

"""Recherche de solutions d'un problème d'optimisation."""

import argparse
import queue
import sys
import threading

from jouets.utils.argparse import analyseur

VERSION = "0.1.0"

def lignes(tableau):
    """Renvoie la représentation du tableau en chaînes, ligne par ligne.

    Ces deux tableaux sont supposés être de taille 9.
    """
    nombres = '{{:>{}}}'.format(max([len(str(x)) for x in tableau]))
    return [
        " | ".join([nombres.format(tableau[3*y+x]) for x in range(0, 3)])
        for y in range(3)
        ]

def juxtapose_tableaux(tableau1, tableau2):
    """Renvoie la chaîne correspondant à la juxtaposition de deux tableaux

    Ces deux tableaux sont supposés être de taille 9.
    """
    return "\n".join([
        "{}       {}".format(ligne1, ligne2)
        for (ligne1, ligne2) in zip(lignes(tableau1), lignes(tableau2))
        ])


class Array(object):
    """Un carré."""

    def __init__(self):
        # Dernier nombre inscrit
        self.score = 0
        # Le contenu
        self.array = [0]*9
        # Nombre de cases vides
        self.empty = 9
        # Historique du remplissage
        self.steps = []

    def fill(self, i):
        """Compléte la case i"""
        self.empty -= 1
        self.steps.append(i)
        prop = sum([self.array[3*x + y]
                    for x in range(i//3-1, i//3+2)
                    for y in range(i%3-1, i%3+2)
                    if (x >= 0 and x < 3) and (y >= 0 and y < 3)
                   ])
        if prop == 0:
            self.array[i] = 1
        else:
            self.array[i] = prop
        self.score = self.array[i]

    def __getitem__(self, i):
        return self.array[i]

    def clone(self):
        """Renvoie une copie de cet objet."""
        clone = Array()
        clone.score = self.score
        clone.array = list(self.array)
        clone.empty = self.empty
        clone.steps = list(self.steps)
        return clone

class Solution(object):
    """Carré en cours de résolution."""

    #: Dictionnaire des cases que l'on peut remplir, et des sous-classes de
    #: :class:`Solution` correspondantes.
    classes = {}

    def __init__(self, cloned=None):
        self.classes = dict([(i, Solution) for i in range(9)])
        if cloned:
            #: Grille
            self.array = cloned.array.clone()
        else:
            self.array = Array()

    def __str__(self):
        return str(self.array)

    def solve(self):
        "Renvoit la liste des objets Solution, après remplissage d'une case."
        return [
            self.classes[i](self).fill(i)
            for i in range(9)
            if ((not self.array[i]) and (i in self.classes))
            ]

    def fill(self, i):
        """Remplit la case i, et renvoit l'objet."""
        self.array.fill(i)
        return self

    @property
    def done(self):
        """Vrai si et seulement si le tableau est complètement rempli."""
        return self.array.empty == 0

    @property
    def score(self):
        """Dernière valeur inscrite dans le tableau."""
        return self.array.score

class SolutionDiagonale(Solution):
    """Solution, dont seules les cases de la diagonales sont remplies."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = dict(
            [(i, SolutionDiagonale) for i in [0, 4, 8]] +
            [(i, Solution) for i in [3, 6, 7]]
            )

class SolutionVerticale(Solution):
    """Solution, dont seules les cases de la colonne centrale sont remplies."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = dict(
            [(i, SolutionVerticale) for i in [1, 4, 7]] +
            [(i, Solution) for i in [0, 3, 6]]
            )

class SolutionCentrale(Solution):
    """Solution, dont seule la case centrale est remplie."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = {
            0: SolutionDiagonale,
            7: SolutionVerticale,
            }

class SolutionVide(Solution):
    """Solution, vide."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes = {
            0: SolutionDiagonale,
            4: SolutionCentrale,
            7: SolutionVerticale,
            }



class Resolution:
    """Calcul des solutions du problème"""

    def __init__(self, nb_process=1):
        self.maximum = 0
        self.lock = threading.Lock()
        self.top = []
        self.nb_process = nb_process

        self.candidats = queue.LifoQueue(0)
        self.candidats.put(SolutionVide())

    def compare(self, solution):
        """Compare 'solution' aux meilleures solutions

        Met à jour la liste des meilleures solutions si nécessaire.
        """
        with self.lock:
            if solution.score == self.maximum:
                self.top.append(solution)
            elif solution.score > self.maximum:
                self.maximum = solution.score
                self.top = [solution]

    def worker(self):
        """Évalue les candidats, tant que cette liste n'est pas vide."""
        while True:
            grille = self.candidats.get()
            if grille.done:
                self.compare(grille)
            else:
                [self.candidats.put(child) for child in grille.solve()] # pylint: disable=expression-not-assigned
            self.candidats.task_done()

    def recherche(self):
        """Recherche les solutions au problème.

        Ne renvoie rien, mais remplit l'attribut `top`.
        """
        for __numero in range(self.nb_process):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()
        self.candidats.join()


    def affiche_solutions(self):
        """Recherche et affiche l'ensemble des solutions du problème."""
        self.recherche()
        solutions = []
        for item in self.top:
            ordre = [0]*9
            for i in range(9):
                ordre[item.array.steps[i]] = i
            solutions.append(juxtapose_tableaux(item.array, ordre))

        print("\n\n".join(solutions))

def _entier_naturel_non_nul(chaine):
    """Renvoie l'entier naturel non nul correspondant à la chaine.

    Lève une exception si la chaine ne représente pas un tel entier.
    """
    if float(chaine) != int(chaine):
        raise argparse.ArgumentTypeError("{} is not an integer.".format(chaine))
    if int(chaine) < 1:
        raise argparse.ArgumentTypeError(
            "{} must be greater than 1.".format(chaine)
            )
    return int(chaine)

def analyse():
    """Renvoie un analyseur de la ligne de commande."""
    parser = analyseur(
        VERSION,
        description=(
            "Solve a game (see documentation for the game description)."
            ),
        epilog=(
            "Two arrays are displayed: the resulting array, and the array of "
            "the steps used to build this resulting array."
            ),
        )
    parser.add_argument(
        '-j', '--jobs', help='Number of jobs to run simultaneously.',
        type=_entier_naturel_non_nul, default=1,
        )
    return parser

def main():
    """Fonction principale"""
    options = analyse().parse_args(sys.argv[1:])
    Resolution(options.jobs).affiche_solutions()
