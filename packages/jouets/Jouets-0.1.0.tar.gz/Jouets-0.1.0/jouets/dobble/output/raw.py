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

"""Affichage brut des cartes, comme une liste de symboles (liste de nombres)."""

def genere(jeu, groupe=False):
    """Renvoit la chaîne correspondant au jeu."""
    cartes = []
    for carte in jeu:
        symboles = []
        for symbole in carte:
            if groupe:
                symboles.append("{}-{}".format(carte.groupe, symbole))
            else:
                symboles.append(str(symbole))
        cartes.append(" ".join(symboles))
    return "\n".join(cartes)

OUTPUT = {
    'raw': {
        'genere': genere,
        'description': "raw list of card numbers",
        },
    }
