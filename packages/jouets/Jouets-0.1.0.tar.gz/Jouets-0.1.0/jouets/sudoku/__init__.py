#!/usr/bin/env python3

# Copyright 2010-2014 Louis Paternault
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

"""Solveur de sudoku"""

import sys

from jouets.sudoku import options
from jouets.sudoku import representation
from jouets.sudoku import resolution
from jouets.sudoku.io import charge_fichier

def main():
    """Fonction principale"""

    commande = options.analyse(sys.argv[1:])
    grille = representation.Grille(charge_fichier(
        commande.fichier,
        commande.format_fichier,
        ))
    commande.traitement.execute_initial()
    resolution.resout(
        grille,
        commande.traitement.execute_courant,
        commande.processus,
        )
    commande.traitement.execute_final()
