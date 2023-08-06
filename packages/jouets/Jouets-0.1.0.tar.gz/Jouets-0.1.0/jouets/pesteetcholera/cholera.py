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
import time
import random

from jouets.pesteetcholera.common import Etat, Terminal, TextInput
from jouets.pesteetcholera.common import analyse, complete_arguments

TITRE = "Choléra"
DEFAUT = {
    "nombre_voisins": 5,
    "proba_contagion": .5,
    "proba_guerison": .8,
    "proba_vaccin": .2,
    "taille_population": 1000,
    "taille_souche": 10,
}

class Population:
    """Population d'individus"""

    def __init__(self, parametres):

        # Définition des paramètres
        self.taille = parametres.taille_population
        self.nombre_voisins = parametres.nombre_voisins
        self.proba_contagion = parametres.proba_contagion
        self.proba_guerison = parametres.proba_guerison
        self.delai = 10**(-parametres.delai/3)

        # Initialisation de la population
        self.population = dict()
        self.population[Etat.malade] = parametres.taille_souche
        self.population[Etat.vaccine] = int(
            parametres.proba_vaccin * self.taille
            )
        self.population[Etat.immunise] = 0
        self.population[Etat.mort] = 0
        self.population[Etat.sain] = (
            self.taille - sum(self.population.values())
            )

    def change_etat(self, etat1, etat2):
        """Change l'état d'un individu"""
        self.population[etat1] -= 1
        self.population[etat2] += 1

    def individu_aleatoire(self):
        """Renvoit l'état d'un individu tiré au hasard dans la population."""
        alea = random.randrange(self.taille)
        for (etat, nombre) in self.population.items():
            if alea < nombre:
                return etat
            alea -= nombre

    def propage(self):
        """Propage l'épidémie"""
        term = Terminal()
        while self.population[Etat.malade]:
            for __ignored in range(self.nombre_voisins):
                voisin = self.individu_aleatoire()
                if (
                        voisin == Etat.sain
                        and
                        random.random() < self.proba_contagion
                    ):
                    self.change_etat(voisin, Etat.malade)
            if random.random() < self.proba_guerison:
                self.change_etat(Etat.malade, Etat.immunise)
            else:
                self.change_etat(Etat.malade, Etat.mort)
            time.sleep(self.delai)
            term.affiche_population(self.population, self.taille)

def analyse_cholera():
    """Renvoit un analyseur de ligne de commande."""
    return analyse(parents=[argparse.ArgumentParser(add_help=False)])

def main():
    """Fonction principale"""
    arguments = complete_arguments(
        analyse_cholera().parse_args(),
        TITRE,
        TextInput,
        DEFAUT,
        )
    Population(arguments).propage()

