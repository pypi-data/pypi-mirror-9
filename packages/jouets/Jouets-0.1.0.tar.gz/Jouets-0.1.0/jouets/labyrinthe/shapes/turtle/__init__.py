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

"""Définitions relatives au labyrinthe utilisant le module turtle"""

#pylint: disable=no-member

import argparse
import functools
import jinja2
import logging
import os
import turtle
import pkg_resources

from jouets.labyrinthe.shapes import load_plugins
from jouets.labyrinthe.base import LabyrintheBase, MurBase, ZoneBase
from jouets.utils.listes import autre
from jouets.utils.turtle import delay

LOGGER = logging.getLogger(__name__)

def complete_analyseur(analyseur, _path, module, parent):
    "Ajoute des options à la ligne de commande, en incluant les sous-modules."
    analyseur_turtle = analyseur.add_parser(
        "turtle",
        help="Two-dimension labyrinths",
        )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '-s', '--size', default=10,
        help='Size of the labyrinth',
        )

    load_plugins(
        analyseur_turtle.add_subparsers(),
        parent + [common],
        os.path.dirname(__file__),
        module + ["turtle"],
        )

class LabyrintheTurtle(LabyrintheBase):
    """Labyrinthe en deux dimensions utilisant le module turtle

    :param fenetre: Taille de la fenêtre, sous la forme d'un ``tuple`` ``(llx,
      lly, urx, ury)`` (voir :mod:`turtle` pour la signification de ces
      coordonnées).
    :type fenetre: tuple
    :param affiche: Vaut ``True`` s'il faut dessiner le labyrinthe au fur et à
      mesure de sa création.
    :type affiche: bool
    """

    def __init__(self, fenetre, affiche):
        super().__init__()

        self.affiche = affiche
        if self.affiche:
            turtle.mode("world")
            turtle.pensize(3)
            (llx, lly, urx, ury) = fenetre
            largeur = urx - llx
            hauteur = ury - lly
            turtle.setworldcoordinates(
                llx - .1 * largeur,
                lly - .1 * hauteur,
                urx + .1 * largeur,
                ury + .1 * hauteur,
                )

    def dessine(self):
        """Dessine le labyrinthe"""
        if self.affiche:
            for mur in self.murs:
                mur.dessine()

    def construit(self):
        """Construit le labyrinthe"""
        if self.affiche:
            with delay(0):
                self.dessine()

        super().construit()

    def fin(self):
        """Attend que l'utilisateur ferme la fenêtre de ``turtle``"""
        super().fin()

        LOGGER.info("End. You can close the main window.")
        if self.affiche:
            turtle.mainloop()

    def export_tex(self, template=None):
        #pylint: disable=maybe-no-member
        if template is None:
            # Using default template
            templatename = pkg_resources.resource_filename(
                "jouets.labyrinthe",
                "data/templates/plain.tex",
                )
            loader = jinja2.FileSystemLoader(os.path.dirname(templatename))
            name = "plain.tex"
        else:
            loader = jinja2.FileSystemLoader(".")
            name = template
        return jinja2.Environment(loader=loader).get_template(name).render(
            {"murs": self.murs}
            )

class MurTurtle(MurBase):
    """Mur en deux dimensions utilisant le module turtle."""

    @property
    def extremites(self):
        """Renvoie les deux etrémités du mur.

        :rtype: tuple
        :return: extrémités, sous la forme d'un ``tuple`` de coordonnées,
          c'est-à-dire de couples de flottants.
        """
        raise NotImplementedError()

    def dessine_zones(self, color1="red", color2="orange"):
        """Dessine deux zones"""
        self.zones[0].dessine(color1)
        self.zones[1].dessine(color2)

    def export_tex(self):
        """Exporte le labyrinthe comme du code TeX."""
        raise NotImplementedError()

class MurSegment(MurTurtle):
    """Mur en forme de segment

    :param pere: Labyrinthe contenant ce mur.
    :type pere: :class:`LabyrintheBase`
    :param tuple p1: Une des extrémités du mur.
    :param tuple p2: L'autre extrémité du mur.
    """

    def __init__(self, pere, p1, p2):
        super().__init__(pere)
        #: Coordonnées du mur
        self.coordonnees = (p1, p2)

    @property
    def extremites(self):
        """Renvoie les coordonnées du mur."""
        return self.coordonnees

    def detruit(self):
        """Détruit le mur"""
        super().detruit()
        self.dessine(color="lightgray")

    def dessine(self, color="black"):
        """Dessine le mur"""
        if self.labyrinthe.affiche:
            turtle.color(color)
            turtle.up()
            turtle.goto(self.extremites[0])
            turtle.down()
            turtle.goto(self.extremites[1])

    def __str__(self):
        return "Mur({}, {})".format(
            self.extremites[0],
            self.extremites[1],
            )

    def export_tex(self):
        """Renvoie le code Tikz correspondant au mur."""
        return r"\draw ({p1[0]}, {p1[1]}) -- ({p2[0]}, {p2[1]});".format(
            p1=self.coordonnees[0],
            p2=self.coordonnees[1],
            )

@functools.total_ordering
class ZoneTurtle(ZoneBase):
    """Implémentation d'une zone plane

    Cette implémentation utilise le module :mod:`turtle`.
    """

    def iter_sommets_murs(self, sommet=None, mur=None):
        """Itérateur sur les couples ``(sommet, mur)`` de la zone.

        L'itérateur garantit que :

        * ``sommet`` est un des sommets de ``mur`` ;
        * tant que c'est possible, les murs sont énumérés de manière
          adjacentes. Ceci n'est pas toujours respecté puisqu'une zone peut
          contenir deux murs non connexes.

        :param sommet: Sommet de départ, sous la forme d'un couple de
          coordonnées (de flottants).
        :type sommet: tuple
        :param mur: Mur de départ.
        :type mur: :class:`MurTurtle`

        * Si ``mur`` est précisé, mais pas ``sommet``, un des sommets du mur
          est choisi arbitrairement comme sommet de départ.
        * Si ``sommet`` est précisé, mais pas ``mur``, un mur adjacent à ce
          sommet est choisi arbitrairement comme mur de départ.
        * Si les deux sont précisés, aucune vérification n'est faite pour
          vérifier que ce sommet est bien adjacent au mur.
        * Si aucun des deux n'est précisé, un couple (adjacent) est pris de
          manière arbitraire.

        .. warning::
            Une zone peut être constituée de deux murs non connexes (si elle
            contient entièrement une autre zone). Dans ce cas, l'itérateur
            passe d'un mur à l'autre sans prévenir.
        """
        murs = list(self.murs_inter()) + list(self.murs_exterieurs())
        if mur is None and sommet is None:
            mur = murs[0]
            sommet = mur.extremites[0]
        elif mur is None and sommet is not None:
            mur = [mur for mur in murs if sommet in mur.extremites][0]
        elif mur is not None and sommet is None:
            sommet = mur.extremites[0]
        else:
            pass
        while murs:
            suivants = [mur for mur in murs if sommet in mur.extremites]
            if suivants:
                mur = suivants[0]
                sommet = autre(mur.extremites, sommet)
            else:
                mur = murs[0]
                sommet = mur.extremites[0]
            murs.remove(mur)
            yield (sommet, mur)

    def iter_sommets(self, debut=None):
        """Itérateur sur les sommets de la zone.

        :param debut: Sommet de départ (sous la forme d'un couple de
          flottants)
        :type debut: tuple

        .. warning::
            Le même avertissement que pour :meth:`iter_sommets_murs` s'applique.
        """
        for (sommet, _mur) in self.iter_sommets_murs(sommet=debut):
            yield sommet

    def iter_murs(self, debut=None):
        """Itérateur sur les murs de la zone

        :param debut: Mur de départ.
        :type debut: :class:`MurTurtle`

        .. warning::
            Le même avertissement que pour :meth:`iter_sommets_murs` s'applique.
        """
        for (_sommet, mur) in self.iter_sommets_murs(mur=debut):
            yield mur


    def __str__(self):
        return "ZoneTurtle({})".format(
            " ".join([str(point) for point in self.iter_sommets()])
            )

    def __lt__(self, other):
        return self.aire < other.aire

    @property
    def aire(self):
        """Renvoie l'aire de la zone.

        .. warning::
            La valeur renvoyée est vraisemblablement fausse dans les cas
            suivants :

            * la zone n'est pas un polygône ;
            * la zone n'est pas connexe.
        """
        #pylint: disable=invalid-name
        somme = 0
        sommets = list(self.iter_sommets())
        (px, py) = sommets[0]
        for (x, y) in sommets[1:] + [sommets[0]]:
            somme += px * y - x * py
            (px, py) = (x, y)
        return abs(somme)



    def dessine(self, color="black"):
        """Dessine la zone

        :param color: Une couleur, telle que reconnue par le module
          :mod:`turtle`, utilisée pour dessiner la zone.
        :type color: str
        """
        if self.labyrinthe.affiche:
            for mur in self.murs_inter():
                mur.dessine(color)
            for mur in self.murs_exterieurs():
                mur.dessine(color)

    def est_valide(self):
        """Renvoie ``True`` si la zone est valide.

        La zone est valide (en plus de la validité de sa classe mère
        :class:`ZoneBase`), si les murs peuvent être correctement énumérés.
        """
        if not super().est_valide():
            return False
        try:
            list(self.iter_sommets_murs())
        except: #pylint: disable=bare-except
            return False
        return True
