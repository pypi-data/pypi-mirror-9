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

"""Création et vérification de jeux de cartes de Dobble"""

import argparse
import functools
import itertools
import sys
import textwrap

from jouets.erathostene import est_premier
from jouets.utils.argparse import analyseur
from jouets.utils.plugins import get_plugin

VERSION = "0.1.0"

@functools.total_ordering
class Carte:
    """Une liste de symboles"""
    # pylint: disable=too-few-public-methods

    def __init__(self, symboles=None, groupe=None):
        self.groupe = groupe
        if symboles is None:
            self.symboles = []
        else:
            self.symboles = list(symboles)

    def __iter__(self):
        for symbol in self.symboles:
            yield symbol

    def __str__(self):
        return " ".join(sorted([str(s) for s in self.symboles]))

    def __lt__(self, other):
        if not isinstance(other, Carte):
            raise TypeError()
        return sorted(self.symboles) < sorted(other.symboles)

    def __eq__(self, other):
        if not isinstance(other, Carte):
            raise TypeError()
        return sorted(self.symboles) == sorted(other.symboles)

    def __hash__(self):
        return hash(str(self))

    def __len__(self):
        return len(self.symboles)

class CarteDobble(Carte):
    """Carte de jeu de Dobble."""
    @property
    def valide(self):
        """Renvoie `True` ssi la carte est valide.

        Une carte est valide si elle ne contient pas de symbole en double.
        """
        return len(set(self.symboles)) == len(self.symboles)

    def est_compatible(self, carte):
        """Renvoie `True` si `self` est compatible avec `carte`.

        Deux cartes sont compatibles si elles ont exactement un symbole en
        commun.
        """
        return len(set(self.symboles) & set(carte.symboles)) == 1

class Jeu:
    """Une liste de cartes"""
    # pylint: disable=too-few-public-methods

    def __init__(self, cartes=None):
        if cartes is None:
            self.cartes = []
        else:
            self.cartes = list(cartes)

    def __iter__(self):
        for carte in self.cartes:
            yield carte

    def __str__(self):
        return "\n".join([str(carte) for carte in sorted(self.cartes)])

    def __eq__(self, other):
        if not isinstance(other, Jeu):
            raise TypeError()
        return sorted(self.cartes) == sorted(other.cartes)

    def __hash__(self):
        return hash(" ".join([str(hash(carte)) for carte in sorted(self)]))

    @property
    def symboles(self):
        """Renvoie l'ensemble des symboles du jeu."""
        symboles = set()
        for carte in self:
            symboles |= set(carte.symboles)
        return symboles

class JeuDobble(Jeu):
    """Jeu de Dobble"""

    def __init__(self, cartes=None):
        super().__init__(cartes)
        self._resume = {
            '_hash': None,
            'valide': None,
            'trivial': None,
            'regulier': None,
            'frequences_symboles': {},
            }
    def _calcule_resume(self):
        """Met à jour, si nécessaire, le résumé du jeu.

        Le « résumé » du jeu est :
        - ses propriétés (valide, trivial, régulier) ;
        - la fréquence d'apparition des symboles.
        """
        if hash(self) != self._resume['_hash']:
            self._resume['_hash'] = hash(self)

        self._resume['valide'] = \
                (not self.cartes_invalides()) and \
                (not self.couples_cartes_invalides())

        self._resume['trivial'] = (
            # Toutes les cartes ne contiennent qu'un symbole
            {len(carte) for carte in self.cartes} == {1}
            and
            # Le jeu est valide
            self._resume['valide']
            )

        frequences = {}
        for carte in self.cartes:
            for symbol in carte:
                frequences[symbol] = frequences.get(symbol, 0) + 1
        self._resume['frequences_symboles'] = frequences

        couples_symboles = [
            (symbole1, symbole2)
            for (symbole1, symbole2)
            in itertools.combinations(frequences.keys(), 2)
            ]
        self._resume['regulier'] = (
            self._resume['valide']
            and
            # Toutes les cartes ont la même taille
            len({len(carte) for carte in self.cartes}) == 1
            and
            # Les symboles apparaissent autant de fois
            len(set(self._resume['frequences_symboles'].values())) == 1
            and
            # Deux symboles quelconques apparaissent sur exactement une carte
            (
                len(frequences) == 1
                or
                set([
                    len([
                        carte
                        for carte in self.cartes
                        if (couple[0] in carte and couple[1] in carte)
                    ])
                    for couple in couples_symboles
                ]) == {1}
                )
            )


    @property
    def valide(self):
        """Retourne `True` ssi le jeu est valide.

        Calcule à nouveau le résumé du jeu si nécessaire.
        """
        self._calcule_resume()
        return self._resume['valide']

    @property
    def regulier(self):
        """Retourne `True` ssi le jeu est régulier.

        Calcule à nouveau le résumé du jeu si nécessaire.
        """
        self._calcule_resume()
        return self._resume['regulier']

    @property
    def trivial(self):
        """Retourne `True` ssi le jeu est trivial.

        Calcule à nouveau le résumé du jeu si nécessaire.
        """
        self._calcule_resume()
        return self._resume['trivial']

    @property
    def frequences_symboles(self):
        """Retourne un dictionnaire des fréquences des symboles.

        Calcule à nouveau le résumé du jeu si nécessaire.

        Les clefs du dictionnaire sont les symboles, et les valeurs sont le
        nombre d'apparition de la clef dans le je.u.
        """
        self._calcule_resume()
        return self._resume['frequences_symboles']

    def cartes_invalides(self):
        """Retourne la liste des cartes invalides."""
        return [carte for carte in self if not carte.valide]

    def couples_cartes_invalides(self):
        """Retourne la liste des couples de cartes incompatibles."""
        return [(card1, card2)
                for (card1, card2) in itertools.combinations(self.cartes, 2)
                if not card1.est_compatible(card2)]

class TailleNonGeree(Exception):
    """Le programme ne sait pas générer de jeu à cette taille."""
    def __init__(self, taille):
        super().__init__()
        self.taille = taille

    def __str__(self):
        return "Size must be a prime number, or 1 ({} is not).".format(
            self.taille
            )

class ErreurSymboles(Exception):
    """Erreur dans la définition des symboles à utiliser."""
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message

def genere_jeu(taille):
    """Crée et retourne un jeu.

    :param int taille: Taille du jeu.
    :return: Un jeu.
    :rtype: :class:`Jeu`
    """
    # Est-ce que je sais générer un jeu de cette taille ?
    if taille != 1 and not est_premier(taille):
        raise TailleNonGeree(taille)

    # Création des `taille×taille` cartes, réparties en `taille` tas de
    # `taille` cartes.
    cartes = [
        [CarteDobble() for x in range(taille)]
        for y in range(taille)
        ]

    dernier = 0

    # Affectation des marqueurs de tas
    marqueurs = list(range(1, taille+1))
    for tas in range(taille):
        for carte in cartes[tas]:
            carte.symboles.append(marqueurs[tas])

    # Affectation des autres symboles des tas (sauf le dernier)
    symboles = [
        list(range(i * taille + 1, (i+1)*taille + 1))
        for i
        in range(1, taille+1)
        ]
    for x in range(taille):
        for y in range(taille):
            for z in range(taille):
                cartes[x][y].symboles.append(symboles[z][(x*z+y) % taille])

    # Créations des cartes de familles de symboles
    cartes.append([
        CarteDobble(famille + [dernier])
        for famille in [marqueurs] + symboles
    ])

    # Création du jeu à partir des cartes
    return JeuDobble(itertools.chain.from_iterable(cartes))


def command_check(arguments):
    """Gestion de la sous-commande 'check'.

    :param arguments: `namespace` renvoyé par :func:`argparse.parse`.
    :return: Le *status code* à retourner par le programme.
    """
    jeu = analyse_fichier(arguments.file)
    if not arguments.show:
        arguments.show = ['valid']
    if not arguments.quiet:

        if 'summary' in arguments.show:
            arguments.show.extend(['trivial', 'regular', 'valid'])
            summary = ""
            summary += "Symbols ({cardinal})".format(
                cardinal=len(jeu.frequences_symboles.keys())
                )
            summary += "".join([
                "\n\t{key}: {value}".format(key=key, value=value)
                for (key, value) in sorted(jeu.frequences_symboles.items())
                ])
            summary += "\n"
            summary += "Cards ({cardinal})".format(cardinal=len(jeu.cartes))
            summary += "".join(["\n\t" + str(carte) for carte in sorted(jeu)])
            summary += "\n"
            cartes_invalides = jeu.cartes_invalides()
            summary += "Invalid cards ({cardinal})".format(
                cardinal=len(cartes_invalides)
                )
            summary += "".join([
                "\n\t" + str(carte)
                for carte in sorted(cartes_invalides)
                ])
            summary += "\n"
            couples_cartes_invalides = jeu.couples_cartes_invalides()
            summary += "Invalid card couples ({cardinal})".format(
                cardinal=len(couples_cartes_invalides)
                )
            summary += "".join([
                "\n\t" + str(card1) + " | " + str(card2)
                for (card1, card2) in sorted(couples_cartes_invalides)
                ])
            print(summary)

    quiet_status = True
    for (check, value) in [
            ('valid', jeu.valide),
            ('regular', jeu.regulier),
            ('trivial', jeu.trivial),
        ]:
        if check in arguments.show:
            quiet_status = quiet_status and value
            print("{}: ".format(check))
            if value:
                print('yes')
            else:
                print('no')

    if not arguments.quiet:
        return 0
    if quiet_status:
        return 0
    else:
        return 1

def analyse_fichier(fileobject):
    """Analyse le fichier donné.

    :param file fileobject: Fichier à analyser.
    :return: Un jeu.
    :rtype: :class:`Jeu`
    """
    jeu = JeuDobble()
    for ligne in fileobject:
        if ligne.strip():
            jeu.cartes.append(CarteDobble(ligne.split()))
    return jeu

def analyse():
    """Renvoie un analyseur de ligne de commande."""
    parser = analyseur(VERSION)
    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True
    subparsers.dest = 'command'

    # Check
    check = subparsers.add_parser(
        'check',
        help='Check properties about the game (default is validity).',
        description='Check properties about the game.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
                Syntax
                  Games are given line per line: each line is a different
                  card (blank lines are ignored). Each card is a white
                  space separated list of symbols (a symbol can be any
                  string not containing white spaces).
                """),
        )
    check.add_argument(
        '-f', '--file',
        nargs='?', type=argparse.FileType('r'), default=sys.stdin,
        help='Input file. Default is standard input.'
        )
    check.add_argument(
        '-r', '--regular',
        dest='show', action='append_const', const='regular',
        help=('Check if game is regular.')
        )
    check.add_argument(
        '-v', '--valid',
        dest='show', action='append_const', const='valid',
        help=('Check if game is valid.'),
        )
    check.add_argument(
        '-t', '--trivial',
        dest='show', action='append_const', const='trivial',
        help=('Check if game is trivial.'),
        )
    check.add_argument(
        '-s', '--summary',
        dest='show', action='append_const', const='summary',
        default=False,
        help='Print somme information about the game.'
        )
    check.add_argument(
        '-q', '--quiet',
        action='store_true',
        help=(
            "Does not print anything: exit status is 0 if condition are met, "
            "1 otherwise."
            )
        )

    # Build
    build = subparsers.add_parser(
        'build',
        help='Build some game.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    build.add_argument(
        '-s', '--size',
        dest='size', action='store', type=int,
        required=True,
        help=('Size of the game.')
        )

    output_plugins = get_plugin('dobble', 'output')
    build.add_argument(
        '-f', '--format',
        choices=output_plugins.keys(),
        default='raw',
        help=(
            "Output format: {}.".format(
                ", ".join([
                    "'{}' ({})".format(keyword, value['description'])
                    for keyword, value
                    in output_plugins.items()
                    ])
            )
        )
        )

    return parser

def main():
    """Fonction principale"""
    # Argument parsing
    arguments = analyse().parse_args(sys.argv[1:])

    # Running subcommands
    if arguments.command == 'check':
        status = command_check(arguments)
    elif arguments.command == 'build':
        print(get_plugin("dobble", "output")[arguments.format]['genere'](
            genere_jeu(arguments.size)
            ))
        status = 0
    else:
        status = 1

    # End
    return status
