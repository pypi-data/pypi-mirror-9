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

"""Génération d'un sous-jeu de base, en utilisant 'algorithme du dobble.
"""

import math

from jouets.dobble import genere_jeu as genere_dobble
from jouets.dobble.memobble import errors
from jouets.dobble.memobble import mmath

def dobble_num(num):
    """Renvoie l'argument de dobble correspondant à un jeu avec `num` symboles.
    """
    delta = 1-4*(1-num)
    if not mmath.est_carre(delta):
        raise errors.TailleNonGeree((
            "Argument '{}' must be one of `p²+p+1`, where `p` is prime."
            ).format(num))
    if not mmath.est_pair(1+int(math.sqrt(delta))):
        raise errors.TailleNonGeree((
            "Argument '{}' must be one of `p²+p+1`, where `p` is prime."
            ).format(num))
    return int((-1+math.sqrt(delta))/2)


def genere(num):
    """Génère un sous-jeu de Mémobble."""
    return genere_dobble(dobble_num(num))

ALGO = {
    'dobble': {
        'genere': genere,
        'default': {
            'num': 7,
            'sub': 4,
            }
        }
    }
