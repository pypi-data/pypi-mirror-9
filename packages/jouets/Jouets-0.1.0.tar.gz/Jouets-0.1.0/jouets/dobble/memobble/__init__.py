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

"""Création et vérification de jeux de cartes de Mémobble"""

import argparse
import functools
import itertools
import math
import os
import pluginbase
import random
import sys
import textwrap

from jouets.dobble import Carte, Jeu
from jouets.dobble.memobble import errors
from jouets.utils.argparse import analyseur
from jouets.utils.plugins import get_plugin

VERSION = "0.1.0"


def analyse():
    """Renvoie un analyseur de ligne de commande."""
    parser = analyseur(VERSION)

    parser.add_argument(
        '-n', '--num',
        type=int,
        default=None,
        help='Number of cards in each sub-game.',
        )

    parser.add_argument(
        '-s', '--sub',
        type=int,
        default=None,
        help="Number of sub-games.",
        )

    parser.add_argument(
        '-a', '--algo',
        choices=['dobble', 'algo1'],
        default='algo1',
        help="Algorithm to use to create each sub-game.",
        )
    parser.add_argument(
        '-r', '--random',
        dest='random', action='store_true',
        default=0,
        help='Random seed.',
        )
    parser.add_argument(
        '-g', '--group',
        action='store_true',
        help='Highlight connex groups of cards.',
        )

    output_plugins = get_plugin('dobble', 'output')
    parser.add_argument(
        '-f', '--format',
        choices=output_plugins.keys(),
        default='raw',
        help=(
            "Output format: {}.".format(
                ", ".join([
                    "'{}' ({})".format(keyword, value['description'])
                    for keyword, value
                    in output_plugins.items()
                    ])
            )
            ),
        )

    return parser

def genere_jeu(algo, sub, num):
    """Génère un jeu."""

    base = get_plugin('dobble.memobble', "algo")[algo]['genere'](num)

    jeu = Jeu()
    symboles = base.symboles
    for i in range(sub):
        for carte in base:
            nouvelle = Carte(groupe=i)
            for symbole in carte:
                nouvelle.symboles.append(symbole + i * len(symboles))
            jeu.cartes.append(nouvelle)

    return jeu

def process_arguments(arguments):
    """Traitement supplémentaire des arguments."""
    default = get_plugin('dobble.memobble', "algo")[arguments.algo]['default']
    if arguments.num is None:
        arguments.num = default['num']
    if arguments.sub is None:
        arguments.sub = default['sub']

    return arguments


def main():
    """Fonction principale"""
    # Argument parsing
    arguments = process_arguments(analyse().parse_args())

    random.seed(arguments.random)
    jeu = genere_jeu(arguments.algo, arguments.sub, arguments.num)

    print(get_plugin('dobble', "output")[arguments.format]['genere'](
        jeu,
        groupe=arguments.group
        ))
