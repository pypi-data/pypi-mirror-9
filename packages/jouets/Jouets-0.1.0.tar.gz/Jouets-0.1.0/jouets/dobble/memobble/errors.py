#!/usr/bin/env python3

# Copyright 2015 Louis Paternault
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

"""Erreurs de Mémobble."""

class ErreurMemobble(Exception):
    """Erreur générique de Mémobble."""
    pass

class TailleNonGeree(ErreurMemobble):
    """Taille de jeu non gérée."""

    def __init__(self, error):
        super().__init__()
        self.message = error

    def __str__(self):
        return self.message

