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

"""Simulation de propagation d'épidémies"""

from collections import namedtuple
from enum import Enum
from functools import total_ordering
from termcolor import colored
import blessings

from jouets.pesteetcholera import VERSION
from jouets.utils import erreurs
from jouets.utils.argparse import analyseur

TypeEtat = namedtuple('TypeEtat', ['indice', 'nom', 'couleur'])


@total_ordering
class Etat(Enum):
    """États d'un individu"""
    #pylint: disable=no-init

    vaccine = TypeEtat(1, "vacciné", "yellow")
    immunise = TypeEtat(2, "immunisé", "green")
    sain = TypeEtat(3, "sain", "blue")
    malade = TypeEtat(4, "malade", "red")
    mort = TypeEtat(5, "mort", "grey")

    @property
    def nom(self):
        """Nom de l'état."""
        return self.value.nom

    @property
    def couleur(self):
        """Couleur associées à l'état"""
        return self.value.couleur

    def __lt__(self, other):
        return self.value.indice < other.value.indice

class Terminal(blessings.Terminal):
    """Gestion de l'affichage dans le terminal"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print()
        print()

    def affiche_population(self, population, taille_max):
        """Affiche les statistiques de la population."""
        formatter = "{{}}: {{:{}}}".format(len(str(taille_max)))
        with self.location(0, self.height-3):
            print(" | ".join([
                colored("█", etat.couleur) + formatter.format(etat.nom, nombre)
                for (etat, nombre)
                in sorted(population.items())
                ]))
        with self.location(0, self.height-2):
            print("".join([
                (colored(
                    "█", etat.couleur) * int(nombre * self.width / taille_max)
                )
                for (etat, nombre)
                in sorted(population.items())
                ]))

class PasUneProbabilite(erreurs.ErreurUtilisateur):
    """Le nombre n'est pas une probabilité."""

    def __init__(self, texte):
        super().__init__(self)
        self.texte = texte

    def __str__(self):
        return (
            "'{}' doit être une probabilité (un nombre entre 0 et "
            "1)."
            ).format(self.texte)

class TextInput:
    """Interface utilisateur en mode console"""
    #pylint: disable=no-init, too-few-public-methods

    @staticmethod
    def numinput(__titre, texte, defaut):
        """Lit un nombre.

        Continue la lecture tant qu'un nombre n'est pas fourni.
        """
        while True:
            try:
                valeur = input("{} [{}]: ".format(texte, defaut))
                if valeur == "":
                    return defaut
                return float(valeur)
            except TypeError:
                pass

def probabilite(text):
    """Renvoit la probabilité correspondant à l'argument, ou lève une exception.
    """
    try:
        proba = float(text)
    except ValueError:
        raise PasUneProbabilite(text)
    if 0 <= proba and proba <= 1:
        return proba
    else:
        raise PasUneProbabilite(text)

def analyse(parents=None):
    """Renvoit un analyseur de ligne de commande."""
    parser = analyseur(VERSION, parents=parents)

    parser.add_argument(
        '-c', '--contagion',
        metavar="PROBA",
        dest="proba_contagion",
        type=probabilite, default=None,
        help=(
            'Probability that sickness will propagate from one person to '
            'another.'
            ),
        )

    parser.add_argument(
        '-V', '--vaccine',
        metavar="PROBA",
        dest="proba_vaccin",
        type=probabilite, default=None,
        help='Probability that a particular person is vaccinated.'
        )

    parser.add_argument(
        '-H', '--heal',
        metavar="PROBA",
        dest="proba_guerison",
        type=probabilite, default=None,
        help=(
            'Probability that a sick person will heal (otherwise, he will '
            'die).'
            ),
        )

    parser.add_argument(
        '-s', '--sick',
        metavar="NUMBER",
        dest="taille_souche",
        type=int, default=None,
        help='Number of sick people in the beginning.'
        )

    parser.add_argument(
        '-p', '--population',
        metavar="NUMBER",
        dest="taille_population",
        type=int, default=None,
        help='Population size.'
        )

    parser.add_argument(
        '-n', '--neighbour',
        metavar="NUMBER",
        dest="nombre_voisins",
        type=int, default=None,
        help='Average number of neighbours of each person.'
        )

    parser.add_argument(
        '-d', '--delay',
        metavar="INT",
        dest="delai",
        type=int, default=5,
        help='Speed (the bigger the faster)'
        )

    return parser

def complete_arguments(arguments, titre, interface, defaut):
    """Complète les arguments manquants, en les demandant à l'utilisateur."""
    for nom, texte in [
            ["taille_population", "Taille de la population"],
            ["taille_souche", "Nombre initial de malades"],
            ["nombre_voisins", "Nombre de voisins"],
        ]:
        while True:
            nombre = getattr(arguments, nom)
            if nombre is not None:
                if 0 < nombre:
                    break
            try:
                setattr(
                    arguments,
                    nom,
                    int(interface.numinput(titre, texte, defaut[nom])),
                    )
            except TypeError:
                raise erreurs.Annule()

    for nom, texte in [
            ["proba_contagion", "Probabilité de contagion"],
            ["proba_guerison", "Probabilité de guérison"],
            ["proba_vaccin", "Probabilité de vaccination"],
        ]:
        while True:
            proba = getattr(arguments, nom)
            if proba is not None:
                if 0 <= proba and proba <= 1:
                    break
            try:
                setattr(
                    arguments,
                    nom,
                    float(interface.numinput(titre, texte, defaut[nom])),
                    )
            except TypeError:
                raise erreurs.Annule()

    return arguments
