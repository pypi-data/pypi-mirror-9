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

"""Création de labyrinthes"""

import argparse
import logging
import random
import sys

from jouets.labyrinthe import shapes
from jouets.utils.argparse import yesno, analyseur
from jouets.utils.erreurs import ErreurInterne

LOGGER = logging.getLogger(__name__)

VERSION = "0.1.0"

def analyse():
    """Renvoie un analyseur de la ligne de commande."""
    parser = analyseur(
        VERSION,
        description="Generate labyrinths",
        )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '--format', '-f',
        choices=['tex'],
        default=None,
        help='Output format',
        )
    common.add_argument(
        '--template', '-t',
        default=None,
        help='Template to use for the LaTeX output format.',
        )
    common.add_argument(
        '--display', '-d',
        choices=['yes', 'no'],
        default='yes',
        help='Display labyrinth building'
        )

    analyseur_formes = parser.add_subparsers(
        title="shapes",
        description="Subcommands providing shapes",
        )
    shapes.load_plugins(analyseur_formes, parent=[common])

    return parser

def main():
    """Fonction principale"""
    options = analyse().parse_args(sys.argv[1:])

    if 'labyrinthe' not in options:
        LOGGER.error('(ERROR) Please choose a labyrinth.')
        sys.exit(1)

    lab = options.labyrinthe(
        taille=int(options.size),
        affiche=yesno(options.display),
        )
    lab.construit()
    if options.format == "tex":
        print(lab.export_tex(options.template))
    lab.fin()
