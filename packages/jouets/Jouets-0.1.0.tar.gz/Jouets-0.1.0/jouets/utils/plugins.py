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

"""Facilite la définition et l'utilisation de plugins."""

import importlib
import os
import pluginbase

def basedir(base):
    """Renvoit le répertoire correspondant au module `base` (relatif à jouets).
    """
    return os.path.dirname(
        importlib.import_module(
            'jouets.{}'.format(base)
            ).__file__
        )

def get_plugin(base, path):
    """Renvoit le dictionnaire de plugins présents dans le chemin ``path``.

    Un plugin est un module contenant un attribut
    ``PATH`` (``path`` en lettres majuscules), de
    type dictionnaire (:type:`dict`).
    """
    plugins = pluginbase.PluginBase(
        package='jouets.{}.{}'.format(base, path),
        )
    plugins = plugins.make_plugin_source(
        searchpath=[os.path.join(
            basedir(base),
            path,
            )],
        persist=True,
        )
    plugin_dict = {}
    for name in plugins.list_plugins():
        plugin = plugins.load_plugin(name)
        try:
            plugin_dict.update(getattr(plugin, path.upper()))
        except KeyError:
            continue
    return plugin_dict

