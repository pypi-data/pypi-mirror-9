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

"""Labyrinthe à base d'un maillage de carrés."""

import itertools

from jouets.labyrinthe.shapes.turtle import \
    LabyrintheTurtle, MurSegment, ZoneTurtle

def complete_analyseur(analyseur, __path, __module, parent):
    """Ajoute des options à la ligne de commande."""
    analyseur_square = analyseur.add_parser(
        "square",
        help="Square basic structure",
        description="Two dimension labyrinth with a square basic structure.",
        parents=parent,
        )
    analyseur_square.set_defaults(labyrinthe=Labyrinthe)

class Labyrinthe(LabyrintheTurtle):
    """Implémentation d'un labyrinthe à base d'un maillage carré.

    :param int taille: Taille du maillage
    :param bool affiche: Même signification que pour
        :class:`~jouets.labyrinthe.shapes.turtle.LabyrintheTurtle`.
    """

    def __init__(self, taille, affiche):
        super().__init__((0, 0, taille, taille), affiche)

        zones = [
            [ZoneTurtle(self) for y in range(taille)]
            for x in range(taille)
            ]
        murs_horizontaux = [
            [MurSegment(self, (x, y), (x+1, y)) for y in range(taille+1)]
            for x in range(taille)
            ]
        murs_verticaux = [
            [MurSegment(self, (x, y), (x, y+1)) for y in range(taille)]
            for x in range(taille+1)
            ]

        #pylint: disable=invalid-name
        for x in range(taille):
            for y in range(taille):
                murs_horizontaux[x][y].affecte_zone(zones[x][y])
                murs_horizontaux[x][y+1].affecte_zone(zones[x][y])
                murs_verticaux[x][y].affecte_zone(zones[x][y])
                murs_verticaux[x+1][y].affecte_zone(zones[x][y])
        self.murs = list(itertools.chain.from_iterable(
            murs_horizontaux + murs_verticaux
            ))
        self.zones = list(itertools.chain.from_iterable(zones))
