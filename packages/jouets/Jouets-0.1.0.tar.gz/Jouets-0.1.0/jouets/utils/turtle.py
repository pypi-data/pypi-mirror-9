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

"""Outils enrichissant le module turtle"""

from contextlib import contextmanager
import turtle

#pylint: disable=no-member
@contextmanager
def delay(temps):
    """Contexte pour changer localement la vitesse de tracé de turtle."""
    vieux = turtle.delay()
    turtle.delay(temps)
    yield
    turtle.delay(vieux)
