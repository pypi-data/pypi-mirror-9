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

"""Quelques exceptions"""

class ErreurInterne(Exception):
    """Erreur interne : le fait qu'elle soit levée constitue un bug."""

    def __str__(self):
        return """Internal error. Please report a bug."""

class ErreurUtilisateur(Exception):
    """Erreur générée par l'utilisateur : afficher le message et quitter."""
    pass

class Annule(ErreurUtilisateur):
    """Annulation par l'utilisateur"""
    pass
