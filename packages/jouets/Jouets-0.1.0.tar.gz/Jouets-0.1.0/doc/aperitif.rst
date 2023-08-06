..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

.. _aperitif:

*************************************************************
`aperitif` — Recherche de solutions au problème des apéritifs
*************************************************************

Description du problème
=======================

Le problème des apéritifs est un problème classique d'algorithmique, illustré
par exemple par `Randall Munroe <http://xkcd.com/287/>`_ (`traduction française
<http://xkcd.lapin.org/index.php?number=287>`_).

Énoncé
------

L'énoncé est le suivant.

* *Version mathématique :* Étant donné un nombre entier :math:`N`, et un
  ensemble :math:`X` de :math:`n` nombres :math:`x_i` (pour :math:`i` entier
  compris entre 0 et :math:`n-1`), quels éléments de :math:`X`, éventuellement
  répétés, ont pour somme :math:`N` ?
* *Version apéritif :* La carte des apéritifs propose un certain nombre
  d'éléments, à des prix différents. Quel assortiment puis-je acheter, coûtant
  *exactement* une certaine somme d'argent :math:`N` ?

C'est une variation du `problème de la somme
<http://fr.wikipedia.org/wiki/Probl%C3%A8me_de_la_somme_de_sous-ensembles>`_.

Difficulté
----------

Ce problème est dit `NP
<http://fr.wikipedia.org/wiki/NP_%28complexit%C3%A9%29>`_ (il est même
`NP-complet <http://fr.wikipedia.org/wiki/NP-complet>`_). Pour simplifier, il
est très difficile à résoudre, dans le sens où si trouver un algorithme de
résolution peut être assez simple, on ne connait pas d'algorithme *efficace*.

Ainsi, le programme que je propose ici fonctionne bien pour de petites valeurs
du problème, mais c'est tout.

Algorithme
==========

Principe
--------

Étant donnés une liste ``prix``, et un ``total`` à atteindre, on fait comme
suit :

* *(lignes 13 à 15)* Si ``prix`` ne contient qu'un élément, et que ``total``
  est un multiple de cet élément, nous avons trouvé une solution.
* *(lignes 17 à 22)* Sinon, on prend le premier élément :math:`x_0` de la
  liste, et on cherche, récursivement, des solutions ne contenant pas cet
  élément, puis le contenant une fois 1, puis 2, etc. puis :math:`n`, (où
  :math:`n` est la partie entière de :math:`\frac{total}{x_0}`).

Code source
-----------

.. literalinclude:: ../jouets/aperitif/__init__.py
    :linenos:
    :pyobject: aperitif
