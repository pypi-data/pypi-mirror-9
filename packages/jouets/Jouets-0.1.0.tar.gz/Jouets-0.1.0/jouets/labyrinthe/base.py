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

"""Définition de classes abstraites de manipulation de labyrinthes."""

import random

from jouets.utils.erreurs import ErreurInterne

class LabyrintheBase:
    """Classe abstraite représentant un labyrinthe"""

    def __init__(self):
        #: Ensemble des murs
        self.murs = set()
        #: Ensemble des zones
        self.zones = set()

    def murs_intra(self):
        """Itérateur sur les murs intérieurs à des zones."""
        for mur in self.murs:
            if mur.est_intra():
                yield mur

    def murs_inter(self):
        """Itérateur sur les murs entre différentes zones."""
        for mur in self.murs:
            if mur.est_inter():
                yield mur

    def murs_exterieurs(self):
        """Itérateur sur les murs extérieurs."""
        for mur in self.murs:
            if mur.est_exterieur():
                yield mur

    def construit(self):
        """Détruit des murs jusqu'à obtention d'un labyrinthe connexe."""
        while list(self.murs_inter()):
            mur = random.choice(list(self.murs_inter()))
            mur.detruit()

    def fin(self):
        """Fonction appelée lorsque le labyrinthe a été généré."""
        pass

    def invalides(self):
        """Renvoie la liste des éléments du labyrinthe invalides.

        :returns: Liste des éléments (murs et zones) invalides.
        :rtype: ``list``

        Cette fonction est utilisée pour les tests.
        """
        a_traiter = list(self.murs) + list(self.zones)
        faits = []
        invalides = []
        while a_traiter:
            element = a_traiter.pop()
            faits.append(element)
            if not element.est_valide():
                invalides.append(element)
            if isinstance(element, MurBase):
                for zone in element.zones:
                    if (zone is not None) and (zone not in faits):
                        a_traiter.append(zone)
            elif isinstance(element, ZoneBase):
                for mur in element.murs:
                    if mur not in faits:
                        a_traiter.append(mur)
        return invalides

    def export_tex(self, template=None):
        """Exporte le labyrinthe comme du code TeX."""
        raise NotImplementedError()

class MurBase:
    """Classe abstraite représentant un mur.

    :param pere: Labyrinthe dans lequel est situé le mur.
    :type pere: :class:`LabyrintheBase`
    """

    def __init__(self, pere):
        #: Zones adjacentes à ce mur. Une zone peut-être égale à ``None`` si le
        #: mur est un mur extérieur.
        self.zones = [None, None]
        #: Labyrinthe dans lequel est situé le mur.
        self.labyrinthe = pere
        self.labyrinthe.murs.add(self)

    def detruit(self):
        """Détruit le mur, et met à jour les zones adjacentes.

        Précondition : le mur est un mur entre deux zones différentes.
        """
        petite, grande = sorted(self.zones)
        grande.absorbe(petite)
        grande.murs.remove(self)
        self.labyrinthe.murs.remove(self)

    def change_zone(self, origine, destination):
        """Met à jour les zones d'un mur.

        :param origine: Zone à supprimer.
        :param destination: Zone par laquelle remplacer ``origine``.
        :type origine: :class:`ZoneBase`
        :type destination: :class:`ZoneBase`

        Remplace ``origine`` par ``destination``, en mettant à jour les
        attribut des zones concernées.
        """
        destination.murs.add(self)
        origine.murs.remove(self)
        for i in range(2):
            if self.zones[i] == origine:
                self.zones[i] = destination

    def affecte_zone(self, zone):
        """Attribue une zone à ce mur.

        :param zone: Zone à attribuer.
        :type zone: :class:`ZoneBase`.
        """
        if (zone is None) and (None in self.zones):
            return
        for i in range(2):
            if self.zones[i] is None:
                self.zones[i] = zone
                zone.murs.add(self)
                return
        raise ErreurInterne()

    def est_inter(self):
        """Renvoie ``True`` si ce mur a deux zones adjacentes"""
        return self.zones[0] != self.zones[1] and not self.est_exterieur()

    def est_intra(self):
        """Renvoie ``True`` si ce mur est interne à une zone"""
        return self.zones[0] == self.zones[1] and not self.est_exterieur()

    def est_exterieur(self):
        """Renvoie ``True`` si ce mur est extérieur"""
        return None in self.zones

    def est_valide(self):
        """Renvoie ``True`` si ce mur est valide.

        Un mur valide est référencé par ses zones adjacentes, et a au moins une
        zone adjacente.
        """
        if len(self.zones) != 2:
            return False
        for zone in self.zones:
            if zone is not None:
                if self not in zone.murs:
                    return False
        return True

class ZoneBase:
    """Représentation d'une zone d'un labyrinthe.

    Une zone est un ensemble connexe du labyrinthe.

    :param pere: Labyrinthe dans lequel est situé le mur.
    :type pere: :class:`LabyrintheBase`
    """

    def __init__(self, pere):
        #: Ensemble des murs (intra et inter zones) adjacents à la zone.
        self.murs = set()
        #: Labyrinthe dans lequel cette zone est située.
        self.labyrinthe = pere
        self.labyrinthe.zones.add(self)

    def absorbe(self, zone):
        """Absorbe la zone ``zone``.

        Cette zone récupère les murs de ``zone``, et cette dernière est
        supprimée.
        """
        copie_murs = zone.murs.copy()
        for mur in copie_murs:
            mur.change_zone(zone, self)
        self.labyrinthe.zones.remove(zone)

    def murs_intra(self):
        """Itérateur sur les murs internes de cette zone."""
        for mur in self.murs:
            if mur.est_intra():
                yield mur

    def murs_inter(self):
        """Itérateur sur les murs de cette zone adjacents à une autre zone."""
        for mur in self.murs:
            if mur.est_inter():
                yield mur

    def murs_exterieurs(self):
        """Itérateur sur les murs extérieurs de cette zone."""
        for mur in self.murs:
            if mur.est_exterieur():
                yield mur

    def est_valide(self):
        """Renvoie ``True`` si cette zone est valide.

        Une zone est valide si elle est référencée par ``self.labyrinthe``, et
        par chacun de ses murs.
        """
        for mur in self.murs:
            if self not in mur.zones:
                return False
        if self not in self.labyrinthe.zones:
            return False
        return True
