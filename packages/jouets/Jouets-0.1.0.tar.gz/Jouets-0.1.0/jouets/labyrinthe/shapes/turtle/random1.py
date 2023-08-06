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

"""Labyrinthe à base d'un maillage aléatoire.

Le rendu n'est pas très utilisable. À améliorer.
"""

import random

from jouets.labyrinthe.shapes.turtle import \
        LabyrintheTurtle, MurSegment, ZoneTurtle
from jouets.utils.listes import autre

def complete_analyseur(analyseur, _path, _module, parent):
    """Ajoute des options à la ligne de commande."""
    analyseur_random1 = analyseur.add_parser(
        "random1",
        help="Random structure",
        description=(
            "Two dimension labyrinth with a random basic structure (I am not "
            "satisfied with the result, though)."
            ),
        parents=parent,
        )
    analyseur_random1.set_defaults(labyrinthe=Labyrinthe)

class Labyrinthe(LabyrintheTurtle):
    """Labyrinthe en deux dimensions à partir d'un maillage aléatoire.

    :param int taille: Taille du maillage
    :param bool affiche: Même signification que pour
        :class:`~jouets.labyrinthe.shapes.turtle.LabyrintheTurtle`.
    """

    #pylint: disable=abstract-class-little-used

    def __init__(self, taille, affiche):
        super().__init__((0, 0, 100, 100), affiche)

        # Rectangle initial
        self.murs.add(MurSegment(self, (0, 0), (0, 100)))
        self.murs.add(MurSegment(self, (0, 100), (100, 100)))
        self.murs.add(MurSegment(self, (100, 100), (100, 0)))
        self.murs.add(MurSegment(self, (100, 0), (0, 0)))
        zone = ZoneTurtle(self)
        for mur in self.murs:
            mur.affecte_zone(zone)
        self.zones = {zone}
        zone.dessine()

        # Partitions aléatoires
        for __ignored in range(taille):
            zone = max(self.zones)
            if len(zone.murs) == 3:
                (mur1, mur2) = random.sample(zone.murs, 2)
            else:
                mur1 = random.choice(list(zone.murs))
                mur2 = random.choice([
                    mur for mur in zone.murs
                    if set(mur.coordonnees).isdisjoint(set(mur1.coordonnees))
                    ])
            self.mur_aleatoire(zone, mur1, mur2)

    @staticmethod
    def point_aleatoire(alea, point1, sommet2):
        "Renvoie un point aléatoire situé sur le segment [`point1`, `point2`]"

        return tuple([
            point1[i] + alea * (sommet2[i] - point1[i]) for i in range(2)
            ])

    def mur_aleatoire(self, zone, mur1, mur2):
        """Construit un mur aléatoire

        :param zone: Zone étant partagée en deux nouvelles zones.
        :type zone: :class:`ZoneBase`.
        :param mur1: Premier mur d'où va partir le nouveau mur.
        :param mur2: Second mur où va arriver le nouveau mur.
        :type mur1: :class:`MurTurtle`
        :type mur2: :class:`MurTurtle`
        """
        (alea1, alea2) = [random.uniform(.2, .8)] * 2 #pylint: disable=unbalanced-tuple-unpacking
        point1 = self.point_aleatoire(alea1, *mur1.extremites)
        point2 = self.point_aleatoire(alea2, *mur2.extremites)

        zonebis = ZoneTurtle(self)
        self.zones.add(zonebis)

        mur1bis = MurSegment(self, mur1.extremites[0], point1)
        mur1.coordonnees = (point1, mur1.extremites[1])
        for element in mur1.zones:
            if element:
                mur1bis.affecte_zone(element)
        self.murs.add(mur1bis)

        #pylint: disable=undefined-loop-variable
        for (point, mur) in zone.iter_sommets_murs(point1, mur1bis):
            if mur == mur2:
                break
            mur.change_zone(zone, zonebis)

        mur2bis = MurSegment(self, point, point2)
        mur2bis.affecte_zone(zone)
        mur2bis.affecte_zone(autre(mur2.zones, zone))
        self.murs.add(mur2bis)

        mur2.coordonnees = [point2, autre(mur.extremites, point)]
        mur2.change_zone(zone, zonebis)

        transversal = MurSegment(self, point1, point2)
        transversal.affecte_zone(zone)
        transversal.affecte_zone(zonebis)
        transversal.dessine()
        self.murs.add(transversal)
