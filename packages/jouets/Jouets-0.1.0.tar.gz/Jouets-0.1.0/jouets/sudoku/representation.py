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

"""Représentation de la grille d'un sudoku.
"""

import collections
import copy
import math
import sys

from jouets.sudoku.io import grille_vierge

def singleton(ensemble):
    """Retourne l'unique élément contenu dans `ensemble`.
    """
    for element in ensemble:
        return element

class Ensemble(collections.MutableSet):
    """Ensemble d'entiers.

    Cette classe définit une suite d'entiers de 0 a `self.__size`
    (`self.__size` étant defini lors de la création de l'objet).

    Aucun test ou supposition n'est faite lors du traitement des donnees sur la
    nature des éléments qui sont ajoutes a l'ensemble. Cette contrainte n'a de
    l'importance que lors de l'affichage (methode __str__).

    :arg list valeurs_initiales: Valeurs initiales de l'ensemble.
    :arg int taille_maximale: Taille maximale de `self`. Si `None`, la taille
        de `valeurs_initiales` est utilisée.
    """
    def __init__(self, valeurs_initiales, taille_maximale=None):
        self.__set = set(valeurs_initiales)
        if taille_maximale:
            self.__size = taille_maximale
        else:
            self.__size = len(valeurs_initiales)

    def add(self, item):
        """Ajoute l'objet `item` à l'ensemble."""
        self.__set.add(item)

    def discard(self, item):
        """Supprime l'objet `item` de l'ensemble."""
        self.__set.discard(item)

    def __iter__(self):
        return iter(self.__set)

    def __len__(self):
        return len(self.__set)

    def __contains__(self, item):
        return item in self.__set

    def __str__(self):
        """Retourne la chaine correspondant a l'ensemble donne en argument

        Precondition:
            "ensemble" est un sous ensemble de l'ensemble des entiers
            inferieurs strictement a self.__size (appele ulterieurement
            "ensemble de reference").

        Pour chaque entier de l'ensemble de reference, dans l'ordre, affiche
        "." si cet entier n'est dans "ensemble", et affiche l'entier en
        question sinon.
        """
        ret = ""
        for element in range(self.__size):
            if element in self.__set:
                ret += str(element)
            else:
                ret += "."
        return ret

    def copy(self):
        """Renvoie une copie de l'objet courant.
        """
        return Ensemble(self.__set, self.__size)

#:  Une contrainte est un couple (fonction, argument) où :
#:
#:  - `fonction`: est une fonction qui definit de quel type de contrainte il
#:    s'agit, et qui servira a appliquer cette contrainte. Cette fonction est
#:    l'une des methode :meth:`Grille.verifie_{case,ligne,colonne,bloc}`.
#:  - `argument`: est l'argument de cette fonction. Sa signification depend de
#:    celle ci. Voir les descriptifs des fonctions en question pour voir la
#:    signification de ces arguments.
Contrainte = collections.namedtuple("Contrainte", "fonction argument")

class Grille:
    #pylint: disable=too-many-instance-attributes
    """Une grille de Sudoku"""

    _old_output = ""
    #: `True` ssi la grille est impossible a resoudre
    impossible = False

    #: `self.possible_case[x][y]` est l'ensemble des entiers possibles pour la
    #: case `(x, y)`
    possible_case = []

    #: `self.possible_ligne[y][valeur]` est l'ensemble des absisses possibles
    #: pour la valeur `valeur` dans la ligne `y`.
    possible_ligne = []

    #: `self.possible_colonne[x][valeur]` est l'ensemble des ordonnees
    #: possibles pour la valeur `valeur` dans la colonne `x`.
    possible_colonne = []

    #: `self.possible_bloc[bloc][valeur]` est l'ensemble des indices possibles
    #: pour la valeur `valeur` dans le bloc `bloc`.
    #: Les blocs sont numerotes dans le sens de lecture courant (de gauche a
    #: droite, puis de haut en bas). De meme pour les indices au sein d'un
    #: bloc
    possible_bloc = []

    #: Nombre de cases dont la valeur n'est pas encore connue
    inconnues = None

    def __init__(self, grille, copie=False):
        #: Ensemble des contraintes a verifier
        self.contraintes = set()

        self.size = int(math.sqrt(len(grille)))
        self.case = copy.deepcopy(grille)
        self.possible_case = grille_vierge(
            self.size**2,
            Ensemble,
            range(self.size**2)
            )
        self.possible_ligne = grille_vierge(
            self.size**2,
            Ensemble,
            range(self.size**2)
            )
        self.possible_colonne = grille_vierge(
            self.size**2,
            Ensemble,
            range(self.size**2)
            )
        self.possible_bloc = grille_vierge(
            self.size**2,
            Ensemble,
            range(self.size**2)
            )
        self.inconnues = self.size**4

        # Initialisation des contraintes
        if not copie:
            for x in range(self.size**2):
                for y in range(self.size**2):
                    if self.case[x][y] is not None:
                        self.affecte((x, y), self.case[x][y])
                        self.inconnues -= 1


    def copy(self):
        """Renvoie une copie de la grille courante
        """
        copie = Grille(self.case, copie=True)
        copie.possible_case = copy.deepcopy(self.possible_case)
        copie.possible_ligne = copy.deepcopy(self.possible_ligne)
        copie.possible_colonne = copy.deepcopy(self.possible_colonne)
        copie.possible_bloc = copy.deepcopy(self.possible_bloc)
        copie.inconnues = self.inconnues
        copie.contraintes = set()
        for cont in self.contraintes:
            if cont.fonction == self.verifie_case:
                fonction = copie.verifie_case
            elif cont.fonction == self.verifie_ligne:
                fonction = copie.verifie_ligne
            elif cont.fonction == self.verifie_colonne:
                fonction = copie.verifie_colonne
            elif cont.fonction == self.verifie_bloc:
                fonction = copie.verifie_bloc
            copie.contraintes.add(Contrainte(fonction, cont.argument))
        return copie

    def affecte(self, coordonnees, valeur):
        """Place `valeur` dans la case de coordonnées `coordonnees`.

        Place les contraintes engendrees dans self.contraintes.
        """
        (x, y) = coordonnees
        if self.case[x][y] == None:
            self.inconnues -= 1
            #sys.stderr.write("%s/%s\n" % (self.inconnues, self.size**4))
        self.case[x][y] = valeur
        self.possible_case[x][y] = Ensemble([valeur], self.size**2)
        # Contraintes initiales
        for autre_valeur in range(self.size ** 2):
            if autre_valeur != valeur:
                self.ajoute_contrainte_case(x, y, autre_valeur)
        for autre_x in range(self.size ** 2):
            if autre_x != x:
                self.ajoute_contrainte_ligne(autre_x, y, valeur)
        for autre_y in range(self.size ** 2):
            if autre_y != y:
                self.ajoute_contrainte_colonne(x, autre_y, valeur)
        (bloc, indice) = self.coordonnees_vers_bloc(x, y)
        for autre_indice in range(self.size ** 2):
            if autre_indice != indice:
                self.ajoute_contrainte_bloc(bloc, autre_indice, valeur)
        if self.inconnues == 0:
            self.contraintes.clear()

    def coordonnees_vers_bloc(self, x, y):
        """Renvoie le tuple (bloc, indice dans bloc) qui correspondent a (x, y).
        """
        return (
            (x // self.size) + (y // self.size) * self.size,
            (x % self.size) + (y % self.size) * self.size
            )

    def bloc_vers_coordonnees(self, bloc, indice):
        """Renvoie les coordonnées qui correspondent aux arguments.
        """
        return (
            self.size * (bloc % self.size) + (indice % self.size),
            self.size * (bloc // self.size) + (indice // self.size)
            )

    def ajoute_contrainte_case(self, x, y, valeur):
        """Supprime "valeur" de self.possible_case[x][y], si necessaire.
        """
        if valeur in self.possible_case[x][y]:
            self.possible_case[x][y].discard(valeur)
            self.contraintes.add(
                Contrainte(self.verifie_case, (x, y, valeur))
                )

    def ajoute_contrainte_ligne(self, x, y, valeur):
        """Supprime "x" de self.possible_ligne[y][valeur], si necessaire
        """
        if x in self.possible_ligne[y][valeur]:
            self.possible_ligne[y][valeur].discard(x)
            self.contraintes.add(
                Contrainte(self.verifie_ligne, (x, y, valeur))
                )

    def ajoute_contrainte_colonne(self, x, y, valeur):
        """Supprime "y" de self.possible_colonne[x][valeur], si necessaire
        """
        if y in self.possible_colonne[x][valeur]:
            self.possible_colonne[x][valeur].discard(y)
            self.contraintes.add(
                Contrainte(self.verifie_colonne, (x, y, valeur))
                )

    def ajoute_contrainte_bloc(self, bloc, indice, valeur):
        """Supprime "indice" de self.possible_bloc[bloc][valeur], si necessaire
        """
        if indice in self.possible_bloc[bloc][valeur]:
            self.possible_bloc[bloc][valeur].discard(indice)
            self.contraintes.add(
                Contrainte(self.verifie_bloc, (bloc, indice, valeur))
                )


    def verifie_case(self, x, y, valeur):
        """`valeur` vient d'etre supprimee de self.possible_case[x][y]
        """
        if len(self.possible_case[x][y]) == 0:
            self.impossible = True
        if len(self.possible_case[x][y]) == 1:
            if self.case[x][y] == None:
                self.affecte((x, y), singleton(self.possible_case[x][y]))
        self.ajoute_contrainte_ligne(x, y, valeur)
        self.ajoute_contrainte_colonne(x, y, valeur)
        (bloc, indice) = self.coordonnees_vers_bloc(x, y)
        self.ajoute_contrainte_bloc(bloc, indice, valeur)

    def verifie_bloc(self, bloc, indice, valeur):
        "`indice` vient d'être supprimé des possibles pour `valeur` dans `bloc`"
        if len(self.possible_bloc[bloc][valeur]) == 0:
            self.impossible = True
        if len(self.possible_bloc[bloc][valeur]) == 1:
            x, y = self.bloc_vers_coordonnees(
                bloc, singleton(self.possible_bloc[bloc][valeur])
                )
            if self.case[x][y] == None:
                self.affecte((x, y), valeur)
        (x, y) = self.bloc_vers_coordonnees(bloc, indice)
        self.ajoute_contrainte_ligne(x, y, valeur)
        self.ajoute_contrainte_colonne(x, y, valeur)
        self.ajoute_contrainte_case(x, y, valeur)

    def verifie_ligne(self, x, y, valeur):
        """`x` vient d'etre supprimee de self.possible_ligne[y][valeur]
        """
        if len(self.possible_ligne[y][valeur]) == 0:
            self.impossible = True
        if len(self.possible_ligne[y][valeur]) == 1:
            if self.case[singleton(self.possible_ligne[y][valeur])][y] == None:
                self.affecte(
                    (singleton(self.possible_ligne[y][valeur]), y),
                    valeur,
                    )
        self.ajoute_contrainte_case(x, y, valeur)
        self.ajoute_contrainte_colonne(x, y, valeur)
        (bloc, indice) = self.coordonnees_vers_bloc(x, y)
        self.ajoute_contrainte_bloc(bloc, indice, valeur)

    def verifie_colonne(self, x, y, valeur):
        """`y` vient d'etre supprimee de self.possible_colonne[x][valeur]
        """
        if len(self.possible_colonne[x][valeur]) == 0:
            self.impossible = True
        if len(self.possible_colonne[x][valeur]) == 1:
            if (
                    self.case[x][
                        singleton(self.possible_colonne[x][valeur])
                        ] == None
                ):
                self.affecte(
                    (x, singleton(self.possible_colonne[x][valeur])),
                    valeur,
                    )
        self.ajoute_contrainte_case(x, y, valeur)
        self.ajoute_contrainte_ligne(x, y, valeur)
        (bloc, indice) = self.coordonnees_vers_bloc(x, y)
        self.ajoute_contrainte_bloc(bloc, indice, valeur)

    def remplit(self):
        """Remplit autant que possible la grille, avec les contraintes connues.

        S'arrete quand plus rien ne peut etre deduit.
        """
        while(len(self.contraintes) > 0) and not self.impossible:
            # Extrait une contrainte
            contrainte = self.contraintes.pop()
            # Applique la contrainte
            contrainte.fonction(*contrainte.argument)

    def __str__(self):
        ret = ""
        for y in range(self.size**2):
            for x in range(self.size**2):
                if self.case[x][y] == None:
                    ret += "."
                else:
                    ret += str(self.case[x][y] + 1)
                ret += " "
        return ret

    def pretty_print(self):
        """Renvoie une chaine representant la grille.
        """
        tableau = [
            [
                0
                for __inutile__ in range(self.size**2)
            ]
            for __inutile__ in range(self.size**2)
        ]
        for x in range(self.size**2):
            for y in range(self.size**2):
                if self.case[x][y] == None:
                    tableau[x][y] = "."
                else:
                    tableau[x][y] = str(self.case[x][y] + 1)
        return self._str_tableau(tableau, croix=True)

    def _str_case(self):
        "Renvoie la chaine de caracteres correspondant à `self.possible_case`."
        return self._str_tableau(self.possible_case, croix=True)

    def _str_colonne(self):
        """Renvoit `self.possible_colonne` sous forme de chaîne de caractères.
        """
        return self._str_tableau(self.possible_colonne, vertical=True)

    def _str_bloc(self):
        "Renvoie la chaine de caracteres correspondant a `self.possible_bloc`."
        copie = [
            [None for __inutile__ in range(self.size**2)]
            for __inutile__ in range(self.size**2)
            ]
        for x in range(self.size**2):
            for y in range(self.size**2):
                bloc, indice = self.coordonnees_vers_bloc(x, y)
                copie[indice][bloc] = self.possible_bloc[y][x]
        return self._str_tableau(copie, croix=True)

    def _str_ligne(self):
        "Renvoie la chaine de caractères correspondant à `self.possible_ligne`."
        return self._str_tableau(
            list(zip(*((self.possible_ligne)))),
            horizontal=True,
            )

    def _str_tableau(self,
                     tableau, croix=False, horizontal=False, vertical=False
                    ):
        """Renvoit la chaîne de caractères correspondant à `tableau`.

        Si croix == True : dessine une croix
        Si horizontal (resp vertical) == True : dessine un quadrillage
        horizontal (resp. vertical)
        """
        max_length = [
            max([
                len(str(tableau[x][y]))
                for x in range(self.size**2)
                ])
            for y in range(self.size**2)
            ]
        ret = ""
        for y in range(self.size ** 2):
            for x in range(self.size ** 2):
                ret += str(tableau[x][y]).center(max_length[y])
                ret += " "
                if (
                        croix
                        and ((x+1) % self.size == 0) and (x != self.size**2 - 1)
                    ) or (
                        vertical and (x < self.size**2 - 1)
                    ):
                    ret += "| "
            ret += "\n"
            if (
                    croix
                    and ((y+1) % self.size == 0) and (y != self.size ** 2 - 1)
                ) or (
                    horizontal and (y < self.size**2 - 1)
                ):
                longueur_ligne = sum(max_length) + self.size**2 - 1
                if croix:
                    longueur_ligne += 2 * (self.size - 1)
                if vertical:
                    longueur_ligne += 2 * (self.size**2 - 1)
                ret += chr(8212) * longueur_ligne
                ret += "\n"
        return ret

    @property
    def resolu(self):
        """Renvoie `True` ssi le sudoku est resolu.
        """
        return self.inconnues == 0

    def print_debug(self):
        """Affiche des informations de débuggage.

        En mettant en valeur ce qui a change depuis le dernier appel a cette
        methode.
        """
        output = ""
        output += str(self) + "\n"

        output += "possible_case" + "\n"
        output += self._str_case() + "\n"

        output += "colonne" + "\n"
        output += self._str_colonne() + "\n"

        output += "ligne" + "\n"
        output += self._str_ligne() + "\n"

        output += "bloc" + "\n"
        output += self._str_bloc() + "\n"

        for indice in range(max(len(self._old_output), len(output))):
            if len(self._old_output) <= indice:
                print(output[indice], end="")
            elif len(output) <= indice:
                print(
                    "\033[42m" + self._old_output[indice] + "\033[0m", end="")
            elif self._old_output[indice] == output[indice]:
                print(output[indice], end="")
            else:
                print("\033[42m" + output[indice] + "\033[0m", end="")

        self._old_output = output

    def cherche_plus_proche(self):
        """Renvoie les coordonnees de la case qui a le moins de candidats

        Les cases ayant 0 candidats ne sont pas considérées.
        """
        x_min, y_min, value_min = 0, 0, self.size**2
        for x in range(self.size**2):
            for y in range(self.size**2):
                value = self.possible_case[x][y]
                if (len(value) < value_min) and (len(value) > 1):
                    x_min, y_min, value_min = x, y, len(value)
        return (x_min, y_min)
