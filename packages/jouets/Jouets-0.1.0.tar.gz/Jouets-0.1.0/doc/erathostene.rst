..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

*******************************************************
`erathostene` — Crible d'Érathostène optimisé en espace
*******************************************************

Le `crible d'Érathostène <http://fr.wikipedia.org/wiki/Crible_d'Érathostène>`_
est un algorithme permettant d'énumérer tous les nombres premiers inférieurs à
un certain nombre :math:`N`. Cette version l'améliore suivant deux aspects :

#. Le nombre maximal n'a pas a être précisé au départ : les nombres premiers
   sont énumérés tant que l'utilisateur n'arrête pas le programme.
#. La mémoire nécessaire est linéaire en le nombre de nombres premiers trouvés,
   et non pas en le plus grand nombre premier. La mémoire nécéssaire `est donc
   <http://fr.wikipedia.org/wiki/Fonction_de_compte_des_nombres_premiers>`_ en
   :math:`O\left(\frac{n}{\ln n}\right)` au lieu de :math:`O(n)` (où :math:`n`
   est le plus grand nombre premier trouvé).

L'algorithme est décrit par la suite (:ref:`erathostene_algo`), et implémenté
dans la fonction :py:func:`premiers`.

Usage
=====

.. argparse::
    :module: jouets.erathostene
    :func: analyse
    :prog: erathostene

.. _erathostene_algo:

Algorithme
==========

Code source
-----------

.. literalinclude:: ../jouets/erathostene/__init__.py
    :linenos:
    :pyobject: premiers

Algorithme d'Érathostène original
---------------------------------

Le principe du crible d'Érathostène est :

#. On considère une table de tous les nombres entiers naturels supérieurs
   (strictement) à 1, jusqu'à un certain :math:`N`.
#. On prend le premier nombre de cette table : il est premier. On le
   supprime, et on supprime également de la table tous ses multiples.
#. On recommence l'étape précédente jusqu'à épuisement de la liste.

Optimisation en espace
----------------------

L'optimisation consiste en la chose suivante. On maintient une liste de
couples :math:`(p, m)` (variable ``prochains``), où :math:`p` est un nombre
premier, et :math:`m` le prochain (nous verrons dans quel sens) de ses
multiples. Ensuite, quand un nombre premier est trouvé, plutôt que de
supprimer tous ses multiples de la table des entiers (qui ne sera donc pas
utile ici), on ajoute à la liste ``prochains`` ce nombre, ainsi que son
prochain multiple.

L'algorithme (de base : quelques optimisations seront apportées dans la
section suivante) est donc le suivant :

1. Initialisation : ``prochains`` contient le couple ``(2, 4)``, et
   ``nombre=3``.

2. On considère ``nombre`` :

  * S'il est une des clefs de la liste ``prochains``, il est donc multiple
    d'un nombre premier : il n'est pas premier. On met à jour le couple
    :math:`(premier, multiple)` rencontré (en le remplaçant par le couple
    :math:`(premier, multiple + premier)`).
  * Sinon, ``nombre`` est premier. On l'affiche à l'utilisateur, et on
    ajoute un couple :math:`(nombre, 2\times nombre)` à la liste
    ``prochains``.

3. On ajoute 1 à ``nombre``, et on recommence à l'étape 2.

Optimisations supplémentaires
-----------------------------

Quelques optimisations sont mises en place.

* Plutôt que de compter de 1 en 1, on remarque que 2 est premier, et on
  compte de 2 en 2, uniquement les nombres impairs (puisqu'aucuns des
  nombres pairs autre que 2 n'est premier). L'initialisation est changée
  également, et on ne considère que les multiples de nombres premiers
  impairs.
* La liste ``prochains`` est triée : cela évite de la parcourir sans arrêt
  (mais il faut tout de même la parcourir pour ajouter de nouveaux éléments
  à la bonne place).
* Le ``multiple`` du couple :math:`(premier, multiple)` n'est pas
  nécéssairement le *prochain* multiple de :math:`premier` si cela n'est
  pas nécessaire. Par exemple, si ``prochains`` contient le couple
  :math:`(3, 15)`, il n'est pas nécessaire d'ajouter :math:`(5, 15)` à la
  liste, puisque 15 est déjà marqué comme non premier ; on ajoutera donc
  plutôt :math:`(5, 25)`.
* Lors du premier ajout d'un nombre premier :math:`p` à la liste
  ``prochains``, le multiple associé est :math:`p^2`. En effet, tous les
  multiples plus petits sont ou seront traités par des nombres premiers
  déjà découverts.

Exemple d'exécution
-------------------

#. Initialisation

    * *(ligne 4)* 2 est un nombre premier et signalé comme tel. Nous ne
      traiterons plus des nombres impairs.
    * *(ligne 5)* 3 est un nombre premier.
    * *(ligne 6)* La liste ``prochains`` est initialisée à ``[(3, 9)]``, le
      multiple suivant, non pair, de 3, étant 9.
    * *(ligne 7)* ``nombre`` est initialisé à 5.

#. Premier passage dans la boucle

    * *(lignes 10 à 13)* Le prochain multiple est 9, donc tous les nombres
      (impairs) de 5 (inclus) à 9 (exclu) sont premiers.
    * *(ligne 12)* Pour chacun de ces nouveaux nombres premiers :math:`p`
      (5 et 7), on ajoute :math:`(p, p^2)` à la liste ``suivants``.
    * La liste ``prochains`` est désormais égale à ``[(5, 25), (7, 49)]``.
    * *(ligne 15)* Le multiple suivant de 3 est 15 (en ignorant 12, pair).
      On l'ajoute à la liste.
    * La liste ``prochains`` vaut désormais ``[(3, 15), (5, 25), (7, 49)]``,
      et ``nombre`` vaut 11.

#. Second passage dans la boucle

    * *(lignes 10 à 13)* Dans la boucle interne, les nombres premiers
      suivants sont découverts : 11 et 13.
    * À la fin de la boucle, on a : ``nombre = 17`` et ``prochains = [(3,
      21), (5, 25), (7, 49), (11, 121), (13, 169)]``.

#. Passages suivants

    * *Troisième :* Les nombres premiers 17 et 19 sont découverts ;
      ``nombre = 23`` et ``prochains = [(5, 25), (3, 27), (7, 49), (11,
      121), (13, 169), (17, 289), (19, 361)]``.
    * *Quatrième :* Le nombre premier 23 est découvert ; ``nombre = 27`` et
      ``prochains = [(3, 27), (5, 35), (7, 49), (11, 121), (13, 169), (17,
      289), (19, 361), (23, 529)]``.
    * *Cinquième :* Aucun nouveau nombre premier ; ``nombre = 29`` et
      ``prochains = [(3, 33), (5, 35), (7, 49), (11, 121), (13, 169), (17,
      289), (19, 361), (23, 529)]``.
    * Etc.
