..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

.. _labyrinthe:

****************************************
`labyrinthe` — Générateur de labyrinthes
****************************************

Description
===========

Voici un programme pour générer aléatoirement des labyrinthes. Comme montré
dans la partie :ref:`algorithmes <labyrinthe_algo>`, l'algorithme lui même est
très simple.

On part d'un ensemble de zones, séparées par des murs. Puis on détruit des
murs les uns après les autres, jusqu'à ce qu'il ne reste plus qu'une zone.

C'est une des méthodes possibles. Elle, ainsi qu'une autre possibilité, est
discutée sur `Wikipédia
<http://fr.wikipedia.org/wiki/Mod%C3%A9lisation_math%C3%A9matique_d%27un_labyrinthe>`_.


.. _labyrinthe_algo:

Algorithme
==========

Une fois débarrassé de toutes les difficultés techniques, l'algorithme est
assez simple, comme le montre le code de la fonction
:meth:`LabyrintheBase.construit`.

.. literalinclude:: ../jouets/labyrinthe/base.py
    :linenos:
    :pyobject: LabyrintheBase.construit

Tant qu'il reste des murs *inter-zones* (c'est-à-dire des murs entre deux
zones différentes), ce qui aurait aussi pu être rédigé comme *tant qu'il reste
plus d'une zone*, on détruit un mur au hasard, ce qui a pour effet de
rassembler deux zones.

Représentation des données
==========================

Un intérêt de l'implémentation faite ici est la liberté qu'elle procure quant
à la forme du labyrinthe : il n'est pas fait la supposition que le labyrinthe
est fait sur la base d'un maillage carré. Une zone est seulement un objet
entouré de murs, et un mur est un objet adjacent à deux zones.

Avec cette représentation, on peut implémenter un labyrinthe plan avec une
base carrée, triangulaire ou aléatoire, mais aussi (je ne l'ai pas
implémenté) un labyrinthe en trois dimensions (ou plus), ou un labyrinthe sur
la surface d'un cube, ou n'importe quoi d'autre.


.. figure:: _images/labyrinthe/triangle.png
  :width: 250px
  :align: left

  Base triangulaire

.. figure:: _images/labyrinthe/random1.png
  :width: 250px
  :align: right

  Base aléatoire

.. figure:: _images/labyrinthe/square.png
  :width: 250px
  :align: center

  Base carrée

Usage
=====

* Génération d'un labyrinthe à base carrée::

    labyrinthe turtle square

* Génération d'un labyrinthe à base triangulaire::

    labyrinthe turtle triangle

* Génération d'un labyrinthe à base aléatoire::

    labyrinthe turtle random1

* D'autres options disponibles. Pour les découvrir::

    labyrinthe [COMMANDE] --help

Documentation des classes de base
=================================

.. automodule:: jouets.labyrinthe.base
  :members:
  :undoc-members:
