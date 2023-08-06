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

"""Outils pour l'analyse des arguments de ligne de commande"""

import argparse
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())

def yesno(texte):
    """Interprète un texte comme un booléen"""
    return texte.lower() in ["y", "yes", "1"]

def analyseur(version, *args, **kwargs):
    """Renvoie un analyseur syntaxique

    Cet analyseur a l'option `--version`.
    """
    parser = argparse.ArgumentParser(*args, **kwargs)
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s {version}'.format(version=version),
        )
    return parser
