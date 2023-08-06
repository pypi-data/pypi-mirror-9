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

"""Crible d'Érathostène optimisé en mémoire"""

import sys

from jouets.utils.argparse import analyseur
from jouets.utils.listes import ListeTriee

VERSION = "0.1.0"

def premiers():
    """Itérateur des nombres premiers"""
    prochains = ListeTriee()
    yield 2
    yield 3
    prochains.push(3, 9)
    nombre = 5
    while True:
        premier, multiple = prochains.pop()
        while multiple != nombre:
            yield nombre
            prochains.push(nombre, nombre**2)
            nombre += 2
        nombre += 2
        prochains.push(premier, prochains.suivant(multiple, 2*premier))

def est_premier(nombre):
    """Renvoie ``True`` si le nombre donné en argument est premier."""
    for i in premiers():
        if i < nombre:
            continue
        if i == nombre:
            return True
        if i > nombre:
            return False

def _affiche_premiers():
    """Affiche les nombres premiers."""
    try:
        for premier in premiers():
            print(premier)
    except KeyboardInterrupt:
        sys.exit(0)
    except BrokenPipeError:
        sys.exit(0)

def analyse():
    """Renvoie un analyseur de la ligne de commande."""
    return analyseur(
        VERSION,
        description="Print primes numbers",
        epilog="This program prints prime numbers until it is killed.",
        )

def main():
    """Fonction principale"""
    analyse().parse_args(sys.argv[1:])
    _affiche_premiers()
