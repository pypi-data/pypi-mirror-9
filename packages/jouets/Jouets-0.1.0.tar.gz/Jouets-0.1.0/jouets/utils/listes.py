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

"""Quelques fonctions utiles manipulant listes et objets apparentés."""

from jouets.utils.erreurs import ErreurInterne

def autre(couple, element):
    """Renvoie l'autre élément du couple.

    :param tuple couple: Couple d'objets.
    :param element: Élement.
    :raises `jouets.utils.erreurs.ErreurInterne`: Si ``element`` n'est pas un
      des deux éléments de ``couple``.
    """
    if couple[0] == element:
        return couple[1]
    elif couple[1] == element:
        return couple[0]
    raise ErreurInterne()

class ListeTriee:
    """Liste triée

    Les objets mis dans la liste sont un couple (valeur, clef). Les valeurs
    sont alors triées selon la clef. La liste est maintenue triée, donc
    obtenir le plus petit élément de la liste est fait en temps contsant.
    """

    def __init__(self):
        self.liste = []

    def push(self, valeur, clef):
        """Insère un élément dans la liste.

        L'élément est ``valeur``, trié selon ``clef``.

        :param object valeur: Élément inséré dans la liste.
        :param int clef: Clef selon laquelle sont triés les éléments.

        Le type de ``valeur`` est libre.
        """
        if not self.liste:
            self.liste.append((valeur, clef))
            return

        (minimum, maximum) = (0, len(self.liste))
        while minimum != maximum:
            moitie = (minimum + maximum) // 2
            if self.liste[moitie][1] < clef:
                minimum = moitie + 1
            else:
                maximum = moitie

        self.liste.insert(minimum, (valeur, clef))

    def pop(self):
        """Retourne (et enlève de la liste) le plus petit élément."""
        return self.liste.pop(0)

    def suivant(self, depart, pas):
        r"""Renvoie la première clef libre de la liste.

        Cette clef libre est le premier entier de la forme :math:`depart + pas
        \times n` (où :math:`n` est dans :math:`\mathbb{N}^*`), tel qu'aucun
        élément de la liste ne corresponde à cette clef.
        """
        candidat = depart
        indice = 0
        while True:
            candidat += pas
            while self.liste[indice][1] < candidat:
                indice += 1
            if self.liste[indice][1] != candidat:
                return candidat

