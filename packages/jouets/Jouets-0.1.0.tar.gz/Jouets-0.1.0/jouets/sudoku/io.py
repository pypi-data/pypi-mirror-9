#!/usr/bin/env python3

# Copyright 2012-2014 Louis Paternault
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

"""Lecture de fichiers représentants des grilles à compléter"""

import math
import textwrap

def grille_vierge(taille, init=None, *args, **kwargs):
    """Renvoit une grille vierge de `taille`×`taille`.

    Si `init` est une fonction, la grille est initialisée avec les valeurs
    `init(*args, **kwargs)` ; sinon, elle est initialisée avec init.
    """
    def valeur_initiale():
        """Renvoit la valeur initiale"""
        if callable(init):
            return init(*args, **kwargs) #pylint: disable=star-args
        else:
            return init
    return [
        [
            valeur_initiale()
            for __inutile__ in range(taille)
        ]
        for __inutile__ in range(taille)
        ]

def charge_fichier_court(fichier):
    #pylint: disable=too-many-branches
    """Lit le fichier, et renvoit une grille (liste de listes) correspondante.

    Le fichier est au format suivant. Les espaces sont ignores. Les retours
    a la ligne sont interdits. Les "." designent des inconnus ::

        ...232....4....1
    """
    grille = None
    taille = None
    for line in fichier:
        if line.isspace():
            continue
        if taille is not None:
            raise Exception(
                "Seule une ligne du fichier peut ne pas etre vide."
                )
        nettoyee = line.strip().replace(" ", "")
        taille = int(math.sqrt(len(nettoyee)))
        grille = grille_vierge(taille)
        x, y = 0, 0
        for char in nettoyee:
            if y == taille**2:
                raise Exception("Trop de caracteres sur la ligne.")
            if char == ".":
                pass
            elif char.isdigit() or (char.isalnum() and char.islower()):
                if char.isdigit():
                    valeur = int(char) - 1
                elif char.isalpha() and char.islower():
                    valeur = ord(char) - 88
                if 0 <= valeur < taille**2:
                    grille[x][y] = valeur
                else:
                    raise Exception(textwrap.dedent("""\
                            Nombre %s trop grand pour la taille de la
                            grille.
                            """ % char))
            else:
                raise Exception(textwrap.dedent("""\
                    Caractere %s interdit. Seuls les chiffres et les lettre
                    minuscules de 'a' a 'z' sont autorisees.
                    """ % char))
            x += 1
            if x == taille:
                x = 0
                y += 1
    return grille

def charge_fichier_long(fichier):
    """Lit le fichier, et renvoit une grille (liste de listes) correspondante.

    Le fichier est au format suivant. Les retours a la ligne sont
    significatifs. Les "." designent des inconnus ::

        . . . 2
        3 2 . .
        . . 4 .
        . . . 1
    """
    lignes = fichier.readlines()
    taille = len(lignes[0].strip().split(" "))
    grille = grille_vierge(taille)
    y = 0
    for line in lignes:
        x = 0
        for word in line.strip().split(" "):
            if word == "":
                continue
            elif x == taille:
                raise Exception(textwrap.dedent("""\
                        Ligne %s trop longue. Je m'attends a des lignes de
                        %s cases.
                        """ % (y+1, taille)))
            elif word == ".":
                pass
            elif not word.isdigit():
                raise Exception(textwrap.dedent("""\
                        La chaine %s (ligne %s) n'est ni un nombre, ni
                        '.'.
                        """ % (word, y+1)))
            else:
                grille[x][y] = int(word) - 1
            x += 1
        if x != taille:
            raise Exception(textwrap.dedent("""\
                Ligne %s trop courte. Je m'attends a des lignes de %s
                cases.
                """ % (y+1, taille)))
        y += 1
        if y == taille:
            break
    return grille

def charge_fichier(fichier, format_fichier):
    """Lit le fichier, et renvoit une liste de listes correspondant.

    :param file fichier: Fichier à lire
    :param str format_fichier: Format du fichier, qui est "short" ou "long".
    """
    if format_fichier == "short":
        return charge_fichier_court(fichier)
    else:
        return charge_fichier_long(fichier)
