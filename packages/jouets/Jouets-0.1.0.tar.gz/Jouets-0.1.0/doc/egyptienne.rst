..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

*****************************************************
`egyptienne` — Décomposition en fractions égyptiennes
*****************************************************

Problème
========

Étant donné une fraction :math:`f` (comprise entre 0 et 1), la décomposition en
fractions égyptiennes revient à écrire cette fraction :math:`f` comme somme de
fractions de numérateur égal à 1, et de dénominateurs différents deux à deux.

Par exemple : :math:`\frac{3}{4}=\frac{1}{2}+\frac{1}{4}`, ou
:math:`\frac{7}{22}=\frac{1}{4}+\frac{1}{5}+\frac{1}{660}`.

Propriétés
==========

Deux questions qui se posent immédiatement sont :

#. Toute fraction (comprise entre 0 et 1) peut elle être décomposée en
   fractions égyptiennes ?
#. Si oui, cette décomposition est-elle unique ?

Les réponses sont oui et non (et une ébauche de démonstration est donnée en
introduction de `cet article
<http://fr.wikipedia.org/wiki/Fraction_%C3%A9gyptienne>`_) :

#. toute fraction peut être décomposée en fractions égyptiennes ;
#. pour chaque fraction, il existe une infinité de telles décompositions.

Algorithme
==========

.. literalinclude:: ../jouets/egyptienne/__init__.py
    :linenos:
    :pyobject: egyptienne

L'algorithme mis en œuvre est un `algorithme glouton
<http://fr.wikipedia.org/wiki/Algorithme_glouton>`_ : étant donné notre
fraction :math:`f`, si elle n'est pas déjà égyptienne (lignes 8 et 9), on
prend comme première fraction égyptienne la plus grosse fraction possible
(inférieure à :math:`f`), et on recommence sur la différence restante (lignes
12 à 15, en remarquant que si :math:`a = n b+r`, alors
:math:`\frac{a}{b}-\frac{1}{n+1}=\frac{a (a-r)}{b (b - r + a)}`).

Optimalité
----------

Si l'on appelle *optimale* une décomposition qui minimise le nombre de termes
de la décomposition, on remarque que l'algorithme n'est pas optimal. Par
exemple, alors qu'il existe une décomposition en deux fractions de
:math:`\frac{9}{20}` (en effet, :math:`\frac{9}{20}=\frac{1}{4}+\frac{1}{5}`),
la décomposition donnée par l'algorithme glouton est
:math:`\frac{9}{20}=\frac{1}{3}+\frac{1}{9}+\frac{1}{180}`).

L'algorithme termine-t-il toujours ?
------------------------------------

Existe-t-il une fraction pour laquelle l'algorithme s'exécute sans jamais
s'arrêter ? La réponse est non, et une démonstration en est donnée `ici
<http://math.univ-lyon1.fr/irem/IMG/pdf/glouton_avec_solutions.pdf>`_.

Usage
=====

.. argparse::
    :module: jouets.egyptienne
    :func: analyse
    :prog: egyptienne

