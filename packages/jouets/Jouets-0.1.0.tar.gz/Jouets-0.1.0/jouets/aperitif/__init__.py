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

"""Résolution (naïve) du problème des apéritifs."""

import os
import sys

from jouets.utils.argparse import analyseur

VERSION = "0.1.0"

def _lire_conf():
    """Lit le fichier de configuration.

    Renvoie, en centimes, la liste des prix définis dans le fichier
    'aperitif.txt'. Renvoie une liste vide si ce fichier n'existe pas.
    """
    try:
        prix = []
        with open(os.path.join(
            os.path.dirname(__file__),
            'aperitif.txt',
            ), 'r') as fichier:
            for ligne in fichier:
                if ligne.strip().startswith('#'):
                    continue
                prix.extend(ligne.replace(',', '.').strip('\n').split(' '))
        return sorted(list(set([
            int(100 * float(item))
            for item
            in prix
            if item
            ])))
    except FileNotFoundError:
        return []

def _lire_prix():
    """Lit la liste des prix.

    Si un tel fichier existe, propose le contenu de 'aperitif.txt' comme
    valeurs par defaut.

    Renvoie, en centimes, la liste des prix.
    """
    try:
        fichier = _lire_conf()
        message = "Liste des prix, separes par des espaces"
        if fichier:
            message += " (laisser vide pour {})".format(", ".join([
                str(float(item)/100)
                for item
                in fichier
                ]))
        message += " ? "
        prix = sorted(list(set([
            int(100 * float(valeur.replace(',', '.')))
            for valeur
            in input(message).split(' ')
            if valeur
            ])), reverse=True)
        if prix:
            return prix
        else:
            return fichier
    except EOFError:
        print()
        return None

def _lire_total():
    """Lit le prix total."""
    print(20*"=")
    try:
        message = "Total (laisser vide pour quitter) ? "
        entree = input(message).replace(',', '.')
    except EOFError:
        print()
        return None
    if not entree.strip():
        return None
    return int(100*float(entree))

def aperitif(total, prix):
    """Iterateur renvoyant les solutions du problème des apéritifs.

    :arg total int: Prix total à atteindre.
    :arg prix list: Liste des prix disponibles.

    :return: Itérateur sur la liste des solutions, ces solutions étant des
             listes correspondant à ``prix``.
    """
    if len(prix) == 0:
        return

    if len(prix) == 1:
        if total % prix[0] == 0:
            yield [int(total // prix[0])]

    for nombre in range(int((total // prix[0])+1)):
        for solution in aperitif(
                total - prix[0]*nombre,
                prix[1:]
            ):
            yield [nombre] + solution

def _chaines_prix(prix):
    """Retourne des chaines de cararctères correspondant aux prix."""
    return [str(float(item)/100) for item in prix]

def _afficher_prix(prix):
    """Affiche la liste des prix, sous forme de tableau."""
    chaines = _chaines_prix(prix)
    longueur = max([len(item) for item in chaines])
    return " | ".join([
        "{{:^{longueur}}}".format(longueur=longueur).format(item)
        for item
        in chaines
        ])

def _afficher_solution(prix, nombre, solution):
    """Affiche une solution, sous forme de tableau.

    Arguments :
    - prix : liste des prix ;
    - nombre : numéro de la solution ;
    - solution : la solution à afficher.
    """
    longueur = max([len(item) for item in _chaines_prix(prix)])
    return "Solution {:^3} : ".format(nombre) + " | ".join([
        "{{:^{longueur}}}".format(longueur=longueur).format(item)
        for item
        in solution
        ])

def boucle():
    """Boucle principale"""
    prix = _lire_prix()
    if prix:
        while True:
            total = _lire_total()
            if total is None:
                break
            print()
            print((" "*len("Solution     : ")) + _afficher_prix(prix))
            nombre = 0
            for solution in aperitif(total, prix):
                nombre += 1
                print(_afficher_solution(prix, nombre, solution))
            if nombre == 0:
                print("*Pas de solutions...*")

def main():
    """Fonction principale."""
    analyseur(VERSION).parse_args(sys.argv[1:])
    boucle()
