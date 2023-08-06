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

import argparse
import collections
import contextlib
import itertools
import logging
import math
import random
import sys
import time
import turtle

from jouets.pesteetcholera.common import Etat, Terminal, TextInput
from jouets.pesteetcholera.common import analyse, complete_arguments
from jouets.utils import erreurs
from jouets.utils.argparse import yesno

LOGGER = logging.getLogger(__name__)

#pylint: disable=no-member

TITRE = "Peste"
DEFAUT = {
    "proba_guerison": .8,
    "nombre_voisins": 5,
    "proba_contagion": .5,
    "proba_vaccin": .2,
    "taille_population": 100,
    "taille_souche": 10,
}

Coordonnees = collections.namedtuple('Coordonnees', ['x', 'y'])

class FauxAffichage:
    """Classe identique à :class:`Affichage`, mais ne faisant rien.

    Utile pour désactiver l'affichage de la propagation de l'épidémie.
    """
    #pylint: disable=no-init

    _quick = 0

    def __init__(self, delai):
        self.delai = 10**(-delai/3)

    @contextlib.contextmanager
    def quick(self):
        """Passe en mode d'affichage rapide."""
        self._quick += 1
        yield
        self._quick -= 1

    def segment(self, *__args, **__kwargs):
        """Fait une pause.

        Cette méthode correspond au tracé d'un segment en mode graphique: il
        faut ici attendre pour que l'animation ne passe pas trop vite.
        """
        if not self._quick:
            time.sleep(self.delai)

    @staticmethod
    def dessine_individu(*__args, **__kwargs):
        """Dessine un individu"""
        pass

    @staticmethod
    def mainloop():
        """Boucle principale."""
        pass

class Affichage(FauxAffichage):
    """Classe gérant l'affichage de la population."""
    # pylint: disable=no-init

    def __init__(self, population, delai):
        super().__init__(delai)
        turtle.setworldcoordinates(-1, -1, population, population)
        turtle.pensize(2)
        turtle.delay(10**((9-delai)/4))

    def segment(self, individu1, individu2, etat):
        """Dessine un segment"""
        # pylint: disable=arguments-differ
        self.invisible_goto(individu1)
        self.__couleur(etat)
        turtle.goto(*individu2.coordonnees)

    def dessine_individu(self, individu):
        """Dessine un individu"""
        # pylint: disable=arguments-differ
        self.invisible_goto(individu)
        self.__couleur(individu.etat)
        turtle.dot(10)

    @contextlib.contextmanager
    def quick(self):
        """Passe momentanément en mode de dessin rapide."""
        delai = turtle.delay()
        turtle.tracer(sys.maxsize, 0)
        yield
        turtle.tracer(1, delai)

    def invisible_goto(self, individu):
        """Se déplace à un endroit sans dessiner."""
        with self.quick():
            turtle.up()
            turtle.goto(*individu.coordonnees)
            turtle.down()

    @staticmethod
    def __couleur(etat):
        """Définit la couleur en fonction de l'état."""
        turtle.color(etat.couleur)

    @staticmethod
    def mainloop():
        return turtle.mainloop()

class Population:
    """Population d'individus."""

    def __init__(self, tortue, parametres):
        self.term = Terminal()
        self.parametres = parametres
        self.tortue = tortue
        self.population = [
            [None for y in range(self.parametres.taille_population)]
            for x in range(self.parametres.taille_population)
            ]
        self.statistiques = dict([(etat, 0) for etat in Etat])
        self.statistiques[Etat.sain] = len(list(
            itertools.chain.from_iterable(self.population)
            ))

        with self.tortue.quick():
            # Création des individus
            for x in range(self.parametres.taille_population):
                for y in range(self.parametres.taille_population):
                    self.population[x][y] = Individu(self, x, y)
                    if random.random() < self.parametres.proba_vaccin:
                        self.population[x][y].etat = Etat.vaccine

            # Création des liens
            for individu in self:
                for voisin in self.proches(individu):
                    if individu not in voisin.voisins:
                        individu.ajoute_voisin(voisin)

            # Dessin des individus (les liens peuvent les avoir partiellement
            # effacés)
            for individu in itertools.chain.from_iterable(self.population):
                individu.dessine()

    def __iter__(self):
        return itertools.chain.from_iterable(self.population)

    def existe(self, x, y):
        """Renvoie ``True`` si si l'individu de coordonnées (x, y) existe.
        """
        if 0 <= x and x < self.parametres.taille_population:
            if 0 <= y and y < self.parametres.taille_population:
                return True
        return False

    def __list__(self):
        return list(itertools.chain.from_iterable(self.population))

    def proches(self, individu):
        """Renvoit les `parametres.nombre_voisins` voisins les plus proches."""
        x = individu.coordonnees.x
        y = individu.coordonnees.y
        proches = []
        for rayon in range(1, self.parametres.taille_population):
            cercle = set()
            for i in range(-rayon, rayon+1):
                for (x_voisin, y_voisin) in [
                        (x-rayon, y+i),
                        (x+rayon, y+i),
                        (x+i, y+rayon),
                        (x+i, y-rayon),
                    ]:
                    if self.existe(x_voisin, y_voisin):
                        if (
                                self.population[x_voisin][y_voisin]
                                not in individu.voisins
                            ):
                            cercle.add(self.population[x_voisin][y_voisin])
            cercle = list(cercle)
            random.shuffle(cercle)
            if len(proches) + len(cercle) <= self.parametres.nombre_voisins:
                proches.extend(cercle)
            else:
                proches.extend(
                    cercle[0:self.parametres.nombre_voisins-len(proches)]
                    )
                return proches
        return proches

    def change_etat(self, etat1, etat2):
        """Change l'état d'un individu."""
        self.statistiques[etat1] -= 1
        self.statistiques[etat2] += 1

    def propage(self, malades):
        """Propage la maladie"""
        for individu in malades:
            individu.etat = Etat.malade

        while malades:
            infecte = malades.pop()
            for voisin in infecte.voisins:
                if random.random() < self.parametres.proba_contagion:
                    if infecte.infecte(voisin):
                        malades.insert(0, voisin)
            if random.random() < self.parametres.proba_guerison:
                infecte.etat = Etat.immunise
            else:
                infecte.etat = Etat.mort
            self.term.affiche_population(
                self.statistiques,
                self.parametres.taille_population**2,
                )



class Individu:
    """Individu d'une population"""

    def __init__(self, population, x, y):
        self.coordonnees = Coordonnees(x, y)
        self._etat = Etat.sain
        self.voisins = []
        self.population = population

        self.dessine()

    def __repr__(self):
        return "Individu({}, {})".format(*self.coordonnees)

    def dessine(self):
        """Dessine l'individu"""
        self.population.tortue.dessine_individu(self)

    @property
    def etat(self):
        """Accesser de l'état"""
        return self._etat

    @etat.setter
    def etat(self, etat):
        """Mutateur de l'état"""
        self.population.change_etat(self._etat, etat)
        self._etat = etat
        self.dessine()

    def ajoute_voisin(self, voisin):
        """Ajoute un voisin à l'individu."""
        self.voisins.append(voisin)
        voisin.voisins.append(self)
        self.population.tortue.segment(
            self,
            voisin,
            Etat.sain
            )

    def infecte(self, voisin):
        """Infecte (peut-être) l'individu.

        Renvoit True si et seulement si l'individu a été infecté.
        """
        if voisin.etat == Etat.sain:
            self.population.tortue.segment(
                self,
                voisin,
                self.etat,
                )
            voisin.etat = Etat.malade
            return True
        return False

def analyse_peste():
    """Renvoit un analyseur de ligne de commande."""
    analyseur_specifique = argparse.ArgumentParser(add_help=False)
    analyseur_specifique.add_argument(
        '-t', '--turtle',
        help="Enable or disable graphical display",
        metavar="BOOLEAN",
        type=yesno,
        default=True,
        )
    return analyse(parents=[analyseur_specifique])

def main():
    """Fonction principale"""

    try:
        arguments = analyse_peste().parse_args()

        if arguments.turtle:
            arguments = complete_arguments(arguments, TITRE, turtle, DEFAUT)
            arguments.nombre_voisins //= 2
            arguments.taille_population = int(
                math.ceil(math.sqrt(arguments.taille_population))
                )
            tortue = Affichage(arguments.taille_population, arguments.delai)
        else:
            arguments = complete_arguments(arguments, TITRE, TextInput, DEFAUT)
            arguments.nombre_voisins //= 2
            arguments.taille_population = int(
                math.ceil(math.sqrt(arguments.taille_population))
                )
            tortue = FauxAffichage(arguments.delai)

        population = Population(tortue, arguments)
        population.propage(
            random.sample(list(population), arguments.taille_souche)
            )
        tortue.mainloop()
    except (erreurs.ErreurUtilisateur, KeyboardInterrupt) as erreur:
        if str(erreur):
            LOGGER.error(str(erreur))
        sys.exit(1)

    sys.exit(0)

