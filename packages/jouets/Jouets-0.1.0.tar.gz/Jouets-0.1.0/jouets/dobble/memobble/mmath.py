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

"""Fonctions mathématiques diverses."""

import math

def est_pair(n):
    """Renvoit vrai ssi le nombre est pair.

    >>> est_pair(1)
    False
    >>> est_pair(2)
    True
    >>> est_pair(3)
    False
    >>> est_pair(4)
    True
    """
    # pylint: disable=invalid-name
    return math.floor(n/2)*2 == n

def est_carre(n):
    """Renvoit vrai ssi le nombre est un carré parfait.

    >>> est_carre(1)
    True
    >>> est_carre(2)
    False
    >>> est_carre(3)
    False
    >>> est_carre(4)
    True
    """
    # pylint: disable=invalid-name
    return math.floor(math.sqrt(n))**2 == n

