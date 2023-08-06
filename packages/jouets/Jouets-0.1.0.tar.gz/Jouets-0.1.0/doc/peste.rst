..
   Copyright 2015 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

.. _peste:

*******************************************
`peste et choléra` — Simulation d'épidémies
*******************************************

Ces deux programmes sont des simulation de propagation d'épidémies. Avant
d'encourager des élèves en TPE à modéliser une telle chose, j'ai voulu tester
ce que cela pourrait donner. Deux versions sont proposées (qui sont sans lien
avec la maladie dont elles portent le nom).

Peste
-----

Dans cette simulation, chaque individu est représenté par le nœud d'un graphe,
relié par une arête à ses voisins, c'est-à-dire aux autres individus qu'il peut
infecter. Il est possible d'afficher ou non le graphe avec l'option
``--turtle``.

.. figure:: _images/peste/peste.png
  :width: 600
  :align: center

Choléra
-------

Cette simulation ne considère pas les personnes individuellement : dans
celle-ci, les informations sont par exemple « 107 personnes sont malades »,
sans savoir précisément quelles sont leurs relations aux autres individus. Il
n'est donc pas possible, contrairement à la simulation ``peste``, d'observer
des effets d'isolation (mise en quarantaine « accidentelle »).

Usage
=====

Les options des deux programmes sont quasiment les mêmes.

Peste
-----

.. argparse::
    :module: jouets.pesteetcholera.peste
    :func: analyse_peste
    :prog: peste

Choléra
-------

.. argparse::
    :module: jouets.pesteetcholera.cholera
    :func: analyse_cholera
    :prog: cholera

