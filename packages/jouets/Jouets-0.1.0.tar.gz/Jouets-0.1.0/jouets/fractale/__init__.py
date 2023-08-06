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

"""Générateur itératif de fractales."""

import logging
import random
import sys
import turtle

from jouets.utils.argparse import analyseur

#pylint: disable=no-member

VERSION = "0.1.0"

LOGGER = logging.getLogger(__name__)

PREDEFINED = {
    'koch': [0, 60, -120, 60],
    }

#pylint: disable=too-few-public-methods
class _Couleur:
    """Gestion des couleurs de la fractale."""

    def __init__(self):
        self.pas = (0, 0, 0)
        self.couleur = list(random.randint(0, 255) for i in range(3))
        turtle.colormode(255)
        while self.pas == (0, 0, 0):
            self.pas = list(random.randint(-2, 2) for i in range(3))
        self.update(0)

    def update(self, compteur):
        """Met à jour la couleur si nécessaire."""
        if compteur == 0:
            self.couleur = list(self.couleur[i] + self.pas[i] for i in range(3))
            for i in range(3):
                if self.couleur[i] > 255 or self.couleur[i] < 0:
                    self.pas[i] = -self.pas[i]
                    self.couleur[i] += self.pas[i]
            turtle.color(self.couleur)

#pylint: disable=too-many-instance-attributes
class _Fenetre:
    """Gestion de la taille de la fenêtre."""

    def __init__(self):
        turtle.mode("world")
        self.llx = 0
        self.lly = 0
        self.urx = 0
        self.ury = 0
        self.f_llx = -1
        self.f_lly = -1
        self.f_urx = 1
        self.f_ury = 1
        turtle.setworldcoordinates(-1, -1, 1, 1)

    def update(self, x, y):
        """Met à jour la taille de la fenêtre si nécessaire."""
        redraw = False
        if x < self.llx:
            self.llx = x
            if x <= self.f_llx:
                self.f_llx = x
                redraw = True
        if x > self.urx:
            self.urx = x
            if x >= self.f_urx:
                self.f_urx = x
                redraw = True
        if y < self.lly:
            self.lly = y
            if y <= self.f_lly:
                self.f_lly = y
                redraw = True
        if y > self.ury:
            self.ury = y
            if y >= self.f_ury:
                self.f_ury = y
                redraw = True
        if redraw:
            turtle.setworldcoordinates(*self.new_coordinates())

    def new_coordinates(self):
        """Calcule la taille de la fenêtre."""
        (largeur_fenetre, hauteur_fenetre) = turtle.screensize()
        largeur = self.urx - self.llx
        hauteur = self.ury - self.lly
        if largeur == 0:
            self.f_llx = -((largeur_fenetre * hauteur) / hauteur_fenetre)/2
            self.f_lly = self.lly
            self.f_urx = ((largeur_fenetre * hauteur) / hauteur_fenetre)/2
            self.f_ury = self.ury
        elif hauteur == 0:
            self.f_llx = self.llx
            self.f_lly = -((hauteur_fenetre * largeur) / largeur_fenetre)/2
            self.f_urx = self.urx
            self.f_ury = ((hauteur_fenetre * largeur) / largeur_fenetre)/2
        else:
            if (largeur_fenetre / largeur) < (hauteur_fenetre / hauteur):
                nouvelle_hauteur = (hauteur_fenetre * largeur) / largeur_fenetre
                self.f_lly = self.lly - ((nouvelle_hauteur - hauteur) / 2)
                self.f_ury = self.ury + ((nouvelle_hauteur - hauteur) / 2)
                self.f_llx = self.llx
                self.f_urx = self.urx
            else:
                nouvelle_largeur = (largeur_fenetre * hauteur) / hauteur_fenetre
                self.f_llx = self.llx - ((nouvelle_largeur - largeur) / 2)
                self.f_urx = self.urx + ((nouvelle_largeur - largeur) / 2)
                self.f_lly = self.lly
                self.f_ury = self.ury

        largeur_fenetre = self.f_urx - self.f_llx
        hauteur_fenetre = self.f_ury - self.f_lly
        self.f_llx -= largeur_fenetre * 0.1
        self.f_lly -= hauteur_fenetre * 0.1
        self.f_urx += largeur_fenetre * 0.1
        self.f_ury += hauteur_fenetre * 0.1
        return self.f_llx, self.f_lly, self.f_urx, self.f_ury

class Fractale:
    """Tracé de fractale"""

    #: Liste des étapes courantes de chaque profondeur de motifs
    compteur = []
    #: Nombre d'angles dans le motif de base
    base = 0
    #: Liste des angles pris par la tortue lors du parcours du motif de base
    angles = []

    def __init__(self, angles):
        self.compteur = [-1]

        self.angles = list(angles)
        self.base = len(angles)
        self.angles.append(-sum(angles))

    def __iter__(self):
        """Itérateur sur les angles à prendre pour tracer la fractale"""
        while True:
            index = 0
            retenue = 1
            angle = 0
            while retenue != 0:
                self.compteur[index] += 1
                angle += self.angles[self.compteur[index]]
                if self.compteur[index] == self.base:
                    self.compteur[index] = 0
                    if index == (len(self.compteur) - 1):
                        self.compteur.append(0)
                    angle += self.angles[self.compteur[index]]
                    index += 1
                    retenue = 1
                else:
                    retenue = 0
            yield angle

def trace(angles, rapide):
    """Trace la fractale

    :param list angles: Liste des angles pris par la tortue.
    :param bool rapide: Tracé rapide ou non.
    """
    # Initialisation
    fractale = Fractale(angles)
    fenetre = _Fenetre()
    couleur = _Couleur()
    if rapide:
        turtle.tracer(fractale.base, 0)
    turtle.title(
        "Fractale — {}".format(" ".join([str(angle) for angle in angles]))
        )

    # Tracé
    for angle in fractale:
        turtle.left(angle)
        turtle.forward(1)
        fenetre.update(turtle.xcor(), turtle.ycor())
        couleur.update(fractale.compteur[0])

def analyse():
    """Renvoie un analyseur de ligne de commande"""
    parser = analyseur(VERSION)

    parser.add_argument(
        '-f', '--fast',
        action='store_true',
        help="Fast drawing."
        )

    parser.add_argument(
        '-t', '--type',
        metavar="NAME",
        action='store',
        choices=PREDEFINED.keys(),
        help="Predefined fractals: 'koch': Koch snowflake,"
        )

    parser.add_argument(
        'angles',
        metavar='angle',
        type=int,
        nargs='*',
        help="Angles of the base drawing of the frarctal.",
        )

    return parser

def main():
    """Fonction principale"""
    arguments = analyse().parse_args(sys.argv[1:])

    angles = arguments.angles
    if arguments.type:
        angles = PREDEFINED[arguments.type]
    if len(angles) < 2:
        LOGGER.error("Please provide at least two angles.")
        return 1

    try:
        trace(angles, rapide=arguments.fast)
    except (KeyboardInterrupt, turtle.TurtleGraphicsError, turtle.TK.TclError):
        return 0
