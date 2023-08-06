..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

****************************
`sudoku` — Solveur de sudoku
****************************

Usage
=====

.. argparse::
    :module: jouets.sudoku.options
    :func: analyseur
    :prog: sudoku

Algorithme
==========

Autres algorithmes
------------------

Je suis loin d'être le seul à m'être intéressé à ce problème, et je suis loin
de proposer la meilleure solution. Par exemple, `Peter Norvig
<http://norvig.com/sudoku.html>`_ a réalisé un solveur de sudoku bien plus
rapide que le mien. En revanche, il ne peut résoudre que des grilles de 9x9.

Représentation des données
--------------------------

Grille
^^^^^^

Une grille de sudoku est représentée par l'objet
:class:`~jouets.sudoku.representation.Grille`, dont un de ses attributs est un
tableau (sous la forme d'une liste de listes) des valeurs de ses cellules
(`None` si elles sont inconnues). Elle contient également un ensemble des
contraintes connues sur la grille, dans l'attribut :attr:`Grille.contraintes`.

Contraintes
^^^^^^^^^^^

Les contraintes sur la grille sont stockées de deux manières différentes.
Celles déjà prises en compte sont stockées dans les attributs
:attr:`Grille.possible_{case,ligne,colonne,bloc}`:

.. py:attribute:: Grille.possible_case

    L'élément `possible_case[x][y]` contient l'ensemble des entiers possibles
    pour la case `(x, y)`. Lorsque cette liste ne contient qu'un élément, cet
    élément peut être attribué à la case.

.. py:attribute:: Grille.possible_ligne

    L'élément `possible_ligne[y][valeur]` contient l'ensemble des absisses
    possibles pour la valeur `valeur` dans la ligne d'abscisse `y`. Lorsque
    cette liste ne contient qu'un élément, `valeur` peut être attribué à la
    case `(x, y)`.

.. py:attribute:: Grille.possible_colonne

    Même fonction que :attr:`Grille.possible_ligne`, pour les colonnes.

.. py:attribute:: Grille.possible_bloc

    L'élément `possible_bloc[bloc][valeur]` contient l'ensemble des indices
    possibles pour `valeur` dans le bloc d'indice `bloc` (un bloc désigne ici
    une carré de la grille devant contenir tous les nombres de 1 à
    :math:`taille^2`).  Lorsque cette liste ne contient qu'un élément, `valeur`
    peut être attribué à la case d'indice correspondant dans le bloc.


Les contraintes en cours de traitement, elles, sont stockées dans l'attribut
:attr:`Grille.contraintes`. Cette liste contient une liste de contraintes à
vérifier. La raison de cette liste (pourquoi les contraintes ne sont-elles pas
reportées immédiatement dans les attributs :attr:`Grille.possible_*` ?) est
expliquée dans la partie suivante.

Recherche de solutions
----------------------

Une file contient l'ensemble des grilles incomplètes à étudier. La résolution,
mise en œuvre dans la fonction :py:func:`~jouets.sudoku.resolution.solveur`
consiste à prendre une grille dans cette liste, et la remplir autant que
possible sans faire d'hypothèses (avec la méthode :py:meth:`Grille.remplit`).
Si la grille est remblie, une solution a été trouvée. Sinon, à partir de la
case qui a le moins de possibilités, mettre dans la file les grilles
correspondant aux hypothèses sur cette case.

.. literalinclude:: ../jouets/sudoku/resolution.py
    :linenos:
    :pyobject: solveur

La fonction :py:meth:`Grille.remplit` prend l'ensemble des contraintes en
attente de traitement (l'attribut :attr:`Grille.contraintes`), et applique les
effets sur la grille. Ces opérations pouvant faire naitre de nouvelles
contraintes, la taille de la boucle n'est pas connue à l'avance. Lorsque la
liste des contraintes est vide, c'est que la grille n'est pas possible, qu'elle
est résolue, ou qu'il est impossible de la remplir davantage sans faire
d'hypothèses.

.. literalinclude:: ../jouets/sudoku/representation.py
    :linenos:
    :pyobject: Grille.remplit
