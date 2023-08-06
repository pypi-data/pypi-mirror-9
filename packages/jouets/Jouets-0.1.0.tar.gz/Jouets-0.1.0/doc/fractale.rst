..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

*************************************************
`fractale` — Tracé de fractale itératif et infini
*************************************************

.. figure:: _images/fractale/koch.png
  :width: 400
  :align: center

Introduction
============

La manière la plus simple de tracer les fractales de type flocon de Koch (voir
ci-dessus) est sans doute la manière récursive suivante ::


    import turtle

    def koch(profondeur):
        if profondeur == 0:
            turtle.forward(10)
        else:
            koch(profondeur - 1)
            turtle.left(60)
            koch(profondeur - 1)
            turtle.right(120)
            koch(profondeur - 1)
            turtle.left(60)
            koch(profondeur - 1)

    koch(5)

L'unique problème que je vois avec cette méthode est qu'il faut définir à
l'avance la profondeur de la fractale. La méthode itérative que je propose
continue à dessiner la fractale tant que l'utilisateur ne l'arrête pas.

Mettons nous bien d'accord : je pense que la méthode itérative mise en œuvre
ici est moins bonne que la méthode récursive habituelle (notamment, je n'ai pas
réussi à dessiner une fractale de type `courbe du dragon
<http://fr.wikipedia.org/wiki/Courbe_du_dragon>`_ ; c'est possible,
mais très technique). Mais j'avais envie de voir ce que ça donnerait.

Description
===========

La fonction effectuant le tracé (ou, selon le point de vue, dirigeant la
tortue) est la fonction :py:func:`trace`, dont le cœur peut être réduit à ::

    fractale = Fractale(angles)
    for angle in fractale:
        turtle.left(angle)
        turtle.forward(1)

La partie intéressante est donc dans l'itérateur de la classe
:py:class:`Fractale`, dont le code est :

.. literalinclude:: ../jouets/fractale/__init__.py
    :linenos:
    :pyobject: Fractale.__iter__


Un fractale est une imbrication d'une infinité de motifs de base imbriqués
les uns dans les autres. L'objet :py:attr:`Fractale.compteur` est une liste
indiquant à quelle étape du motif de base est en cours de dessin, suivant la
profondeur du motif considéré.

.. figure:: _images/fractale/etapes.png
  :width: 400
  :align: right

Par exemple (sur la figure ci-contre), ce compteur valant ``[1, 3, 2]``
indique que la fractale en est à :

* la seconde étape (1) du motif le plus profond (en bleu),
* la quatrième étape (3) du motif supérieur (en vert),
* la troisième étape (2) du plus grand motif (en rouge).
* et, implicitement, la première étape (0) de tous les motifs de taille
  supérieure.

Le calcul de l'angle pris par la tortue à chaque étape se fait alors
simplement en ajoutant les angles des étapes des motifs ayant évolué.

Usage
=====

.. argparse::
    :module: jouets.fractale
    :func: analyse
    :prog: fractale
