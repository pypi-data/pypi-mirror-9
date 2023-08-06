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

"""Labyrinthe à base d'un maillage de triangles."""

from math import sqrt
import itertools

from jouets.labyrinthe.shapes.turtle import \
        LabyrintheTurtle, MurSegment, ZoneTurtle

def complete_analyseur(analyseur, _path, _module, parent):
    """Ajoute des options à la ligne de commande."""
    analyseur_triangle = analyseur.add_parser(
        "triangle",
        help="Triangle basic structure",
        description="Two dimension labyrinth with a triangle basic structure.",
        parents=parent,
        )
    analyseur_triangle.set_defaults(labyrinthe=Labyrinthe)

class Labyrinthe(LabyrintheTurtle):
    """Implémentation d'un labyrinthe à base d'un maillage carré.

    :param int taille: Taille du maillage
    :param bool affiche: Même signification que pour
        :class:`~jouets.labyrinthe.shapes.turtle.LabyrintheTurtle`.
    """

    def __init__(self, taille, affiche):
        super().__init__((0, 0, taille, taille * sqrt(3)/2), affiche)

        zones_gauche = [
            [ZoneTurtle(self) for y in range(taille - x)]
            for x in range(taille)
            ]
        zones_droite = [
            [ZoneTurtle(self) for y in range(taille - x - 1)]
            for x in range(taille - 1)
            ]
        murs_bas = [
            [MurSegment(
                self, (x + .5*y, y*sqrt(3)/2), (x+1 + .5*y, y*sqrt(3)/2)
                )
             for y in range(taille - x)]
            for x in range(taille)
            ]
        murs_montant = [
            [MurSegment(
                self, (x + .5*y, y*sqrt(3)/2), (x+.5*y+.5, (y+1)*sqrt(3)/2)
                )
             for y in range(taille - x)]
            for x in range(taille)
            ]
        murs_descendant = [
            [MurSegment(
                self, (x + .5*y+.5, (y+1)*sqrt(3)/2), (x+1+.5*y, y*sqrt(3)/2)
                )
             for y in range(taille - x)]
            for x in range(taille)
            ]

        #pylint: disable=invalid-name
        for x in range(taille):
            for y in range(taille - x):
                murs_bas[x][y].affecte_zone(zones_gauche[x][y])
                murs_montant[x][y].affecte_zone(zones_gauche[x][y])
                murs_descendant[x][y].affecte_zone(zones_gauche[x][y])
                if x + y != taille - 1:
                    murs_bas[x][y+1].affecte_zone(zones_droite[x][y])
                    murs_montant[x+1][y].affecte_zone(zones_droite[x][y])
                    murs_descendant[x][y].affecte_zone(zones_droite[x][y])

        self.murs = list(itertools.chain.from_iterable(
            murs_bas + murs_montant + murs_descendant
            ))
        self.zones = list(itertools.chain.from_iterable(
            zones_gauche + zones_droite
            ))
