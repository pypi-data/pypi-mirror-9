..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

************************************************
`dobble` — Création de jeu de cartes de *Dobble*
************************************************

Le `Dobble <http://www.asmodee.com/ressources/jeux_versions/dobble.php>`__ est
un jeu de société de rapitidé, dont les règles s'expliquent en moins de vingt
secondes (sans exagérer). Il se compose de 55 cartes comportant chacune huit
symboles, ayant la particularité suivante : deux cartes quelconques ont
exactement un symbole en commun (ni plus ni moins).

La question qui se pose immédiatement est : comment créer un tel jeu de
cartes ? L'analyse mathématique, et la description de l'algorithme, sont
proposés dans la partie :ref:`dobble_math`.

Ce programme permet de générer des jeux de cartes, de taille arbitrairement
grande (mais pas arbitraire pour autant), et de vérifier qu'un jeu donné est
correct.

Table des matières
------------------

La première partie :ref:`dobble_math` propose une analyse mathématique du jeu,
ainsi qu'une description et preuve de l'algorthme. La seconde partie
:ref:`dobble_variantes` contient l'analyse mathématique de deux variantes
possibles à ce jeu. La dernière, :ref:`dobble_usage`, enfin, décrit
l'utilisation du programme en lui-même.

.. toctree::
   :maxdepth: 2
   :numbered:

   dobble/math
   dobble/variantes
   dobble/usage


Autres analyses
---------------

L'analyse semblant faire référence sur internet est proposée par le Maxime
Bourrigan (du CNRS) : `Dobble et la géométrie finie
<http://images.math.cnrs.fr/Dobble-et-la-geometrie-finie.html>`_. Dans cet
article, l'auteur utilise une approche géométrique pour étudier ce jeu, mais
sans proposer d'algorithme pour générer de jeu.

Bourrigan apporte une information très intéressante concernant ce genre de
problèmes : l'ensemble des configurations possibles est mal connu, et
l'existence d'un jeu à 157 cartes (ayant chacune 13 symboles) est un problème
ouvert.

Notre proposition, quant à elle, utilise une approche arithmétique. Je ne suis
pas le premier à découvrir la méthode que je propose ici : une rapide recherche
de `math dobble` sur votre moteur de recherche préféré vous donnera d'autres
exemples. Les cas de découvertes simultanées sont monnaie courante en sciences,
et je suppose que l'aspect mathématique de ce jeu a été perçu par de nombreux
joueurs, qui ont alors joué à en étudier les propriétés.


