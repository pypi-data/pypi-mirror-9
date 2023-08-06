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

"""Manipulation des modules implémentant des formes de labyrinthes"""

import glob
import importlib
import logging
import os
import traceback

LOGGER = logging.getLogger(__name__)

def load_plugins(analyseur, parent, path=None, module=None):
    """Charge les plugins de formes, en enrichit ``analyseur``.

    :param analyseur: Objet retourné par un appel à
        `ArgumentParser.add_subparser()
        <https://docs.python.org/3.4/library/argparse.html#sub-commands>`_.
        Cet objet va être enrichi par les différents plugins chargés pour
        ajouter les options à la ligne de commande.
    :param parent: `Analyseur parent
        <https://docs.python.org/3.4/library/argparse.html#parents>`_, destiné
        à être inclus par les sous-commandes.
    :param path: Chemin du répertoire à inclure (sous la forme d'une chaîne
        ``str``).
    :type path: str
    :param module: Module, sous la forme d'une liste, correspondant à ``path``.
    :type module: list
    """
    if path is None:
        path = os.path.dirname(__file__)
    if module is None:
        module = ['jouets', 'labyrinthe', 'shapes']
    for nom in os.listdir(path):
        if os.path.isdir(os.path.join(path, nom)):
            if os.path.exists(os.path.join(path, nom, "__init__.py")):
                pass
            else:
                continue
        else:
            if (
                    os.path.basename(nom).endswith('.py')
                    and os.path.basename(nom) != "__init__.py"
                ):
                nom = os.path.basename(nom)[:-len('.py')]
            else:
                continue

        try:
            plugin = importlib.import_module(
                ".".join(module + [nom]),
                )
        except Exception as erreur: #pylint: disable=broad-except
            LOGGER.warning(
                "Plugin '{}' could not be loaded. Ignored:".format(
                    os.path.basename(nom)
                    )
                )
            LOGGER.warning(
                "> ".join(
                    traceback.format_exception(type(erreur), erreur, None)
                    )
                )
        else:
            plugin.complete_analyseur(analyseur, path, module, parent)
