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

#pylint: disable=invalid-name

"""Décomposition en fractions égyptiennes."""

import sys

from jouets.utils.argparse import analyseur

VERSION = "0.1.0"

def pgcd(a, b):
    """Renvoie le PGCD de ``a`` et ``b``

    L'algorithme mis en œuvre est celui d'`Euclide
    <http://fr.wikipedia.org/wiki/Algorithme_d%27Euclide>`_.
    """
    if a < b:
        return pgcd(b, a)
    r = a % b
    if r == 0:
        return b
    return pgcd(b, r)

def irreductible(a, b):
    """Simplifie la fraction ``a/b``.

    Renvoie un couple ``(numérateur, dénominateur)``.
    """
    n = pgcd(a, b)
    return (a//n, b//n)

def egyptienne(a, b):
    """Décompose ``a/b`` en fraction égyptienne.

    Renvoie la liste des dénominateurs de la décomposition.
    """
    (a, b) = irreductible(a, b)

    if a == 1:
        return [b]

    (n, r) = divmod(b, a)
    return [n+1] + egyptienne(
        a * (a - r),
        b * (b - r + a),
        )

def _print_egyptienne(a, b, denominateurs):
    """Affiche la fraction et sa décomposition."""
    print("{}/{} = {}".format(
        a,
        b,
        " + ".join(
            ["1/{}".format(n) for n in denominateurs]
        ),
        ))

def analyse():
    """Renvoie un analyseur de la ligne de commande."""
    parser = analyseur(
        VERSION,
        description="Calculate egyptian fractions",
        )
    parser.add_argument(
        'fraction', metavar='A/B', nargs='+', type=str,
        help=(
            "Fractions to decompose, in the form 'a/b' (where a and b are "
            "integers)."
        )
    )
    return parser

class _ErreurOptions(Exception):
    """Erreurs dans les options de la ligne de commande."""

    def __init__(self, fraction):
        super().__init__(self)
        self.fraction = fraction

    def __str__(self):
        return (
            "Error: Fraction '{}' is not of the form INT/INT (where the "
            "second int is not zero)."
            ).format(self.fraction)

def _analyse_fraction(texte):
    """Analyse une fraction, telle qu'entrée dans la ligne de commandes.

    Le texte doit être de la forme *INT/INT*, où *INT* sont des entiers, le
    second étant non nul.

    Renvoie le couple ``(numérateur, dénominateur)`` correspondant à la
    fraction.

    Lève une exception *_ErreurOptions* si le format attendu n'est pas
    respecté.
    """
    liste = texte.split('/')
    if len(liste) != 2:
        raise _ErreurOptions(texte)

    try:
        (a, b) = [int(n) for n in liste]
    except ValueError:
        raise _ErreurOptions(texte)

    if b == 0:
        raise _ErreurOptions(texte)

    return (a, b)

def main():
    """Fonction principale

    Prend en argument les arguments de la ligne de commande.
    """
    for fraction in analyse().parse_args(sys.argv[1:]).fraction:
        try:
            (a, b) = _analyse_fraction(fraction)
        except _ErreurOptions as erreur:
            sys.stderr.write(str(erreur) + "\n")
            continue

        _print_egyptienne(
            a, b,
            egyptienne(a, b)
            )
