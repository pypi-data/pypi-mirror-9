..
   Copyright 2014 Louis Paternault
   
   Cette œuvre de Louis Paternault est mise à disposition selon les termes de
   la licence Creative Commons Attribution - Partage dans les Mêmes Conditions
   4.0 International (CC-BY-SA). Le texte complet de la licence est disponible
   à l'adresse : http://creativecommons.org/licenses/by-sa/4.0/deed.fr

**********************************************
`chemin` — Recherche du score maximal d'un jeu
**********************************************

Usage
=====

.. argparse::
    :module: jouets.chemin
    :func: analyse
    :prog: chemin


Description du jeu
==================

Dans un carré 3x3, on remplit une à une les 9 cases, avec la règle suivante :
    * si toutes les cases entourant la case sont vides, inscrire 1 ;
    * sinon, inscrire la somme des nombres présents dans toutes les cases
      adjacentes (diagonales incluses).

Le jeu se termine lorsque toutes les cases sont pleines, et le score est la
plus grande valeur écrite dans le tableau.

Voici un exemple de jeu, avec un score de 33 :

+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+
| .. math::                           | .. math::                           | .. math::                           | .. math::                           | .. math::                           | .. math::                           | .. math::                           | .. math::                           | .. math::                           |
|     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |     :nowrap:                        |
|                                     |                                     |                                     |                                     |                                     |                                     |                                     |                                     |                                     |
|     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |     \begin{array}{|c|c|c|}          |
|         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |
|         \color{red}{1}  & ~~ &   \\ |         1  &    & ~~\\              |         1  & \color{red}{2}  & ~~\\ |         1  & 2  & \color{red}{3} \\ |         1  & 2  & 3 \\              |         1  & 2  & 3 \\              |         1  & 2  & 3 \\              |         1  & 2  & 3 \\              |         1  & 2  & 3 \\              |
|         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |
|            &    & ~~\\              |            & \color{red}{1}  &   \\ |            & 1  &   \\              |            & 1  &   \\              |            & 1  & \color{red}{6} \\ |            & 1  & 6 \\              |            & 1  & 6 \\              |            & 1  & 6 \\              |         \color{red}{33} & 1  & 6 \\ |
|         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |
|            &    &   \\              |            &    &   \\              |            &    &   \\              |            &    &   \\              |            &    &   \\              |            &    & \color{red}{7} \\ |            & \color{red}{14} & 7 \\ |         \color{red}{15} & 14 & 7 \\ |         15 & 14 & 7 \\              |
|         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |         \hline                      |
|     \end{array}                     |     \end{array}                     |     \end{array}                     |     \end{array}                     |     \end{array}                     |     \end{array}                     |     \end{array}                     |     \end{array}                     |     \end{array}                     |
+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+-------------------------------------+

La question que l'on se pose est : quel est le score maximal possible ?

Recherche de solution optimale
==============================

Premières propriétés
--------------------

Cette partie manque un peu de rigueur, c'est la raison pour laquelle les
démonstrations ne sont présentées que comme des ébauches.

.. proof:definition:: Solutions

    * On appelle *solution* l'ordre dans lequel on remplit la grille.
    * On dit qu'une solution est *(strictement) supérieure* à une autre si le
      score de la première est (strictement) supérieur au score de la seconde.
    * On appelle *solution maximale* une solution supérieure à toutes les
      solutions possibles.
    * Une *case réalisant le score* d'une solution est une case de la grille
      complétée contenant la plus grande valeur de la grille (donc le score).

Dans la méthode :meth:`Solution.score`, la valeur de la dernière case remplie
est prise comme le score de cette grille. Deux questions se posent alors.

  - Le score maximal calculé risque-t-il d'être faux, si le score maximal n'est
    jamais atteint par la dernière case ?
  - Si le score maximal est atteint par la dernière case dans au moins une des
    grilles, des grilles maximales risquent-elles d'être oubliées, si la case
    remplissant leur score maximale n'est pas la dernière case remplie ?

Heureusement, la réponse est non :

.. proof:property::

    Une solution dont la dernère case remplie ne réalise pas le score n'est
    pas maximale.

.. proof:proof:: ébauche

    Supposons qu'il existe une solution :math:`S`, maximale, dont la dernière
    case remplie ne réalise pas le score.

    Soit :math:`S'` la nouvelle solution, identique à :math:`S`, sauf que les
    cases remplies après la (ou les) cases réalisant le score sont cette fois ci remplies
    en premier. Appellons :math:`p'` la première case remplie de :math:`S'`,
    :math:`m` la case de :math:`S` réalisant le score maximal, et :math:`d'` la dernière
    case de :math:`S'` remplie (qui correspond donc à :math:`m`).

    Vu la taille de la grille, :math:`p'` et :math:`d'` sont soit adjacentes,
    soient séparées par une case.

    * Si :math:`p'` et :math:`d'` sont adjacentes, alors la valeur de
      :math:`d'` est supérieure ou égale à la valeur de :math:`m`, à laquelle
      on ajoute la valeur :math:`p'` (soit 1). La valeur de :math:`p'` est donc
      strictement supérieure à :math:`m`, et le score de :math:`S'` est
      strictement supérieur au score de :math:`S`, qui n'est donc pas maximal,
      ce qui est contraire à l'hypothèse de départ.
    * Si :math:`p'` et :math:`d'` sont séparées par une case :math:`c'`. Alors
      avec un raisonnement similaire, on montre que la valeur de cette case
      dans :math:`S'` est strictement supérieure à la valeur de la case
      correspondante dans :math:`S`, donc que la valeur de :math:`p'` est
      strictement supérieure à celle de :math:`m`, donc que le score de
      :math:`S'` est strictement supérieur à celui de :math:`S`, et donc que
      :math:`S` n'est pas maximale, ce qui est contraire à l'hypothèse de
      départ.

    L'hypothèse de départ est donc fausse, et une solution dont la dernière
    case remplie ne réalise pas le score n'est pas possible.

Donc l'approximation faite dans la méthode :meth:`Solution.score`, en
considérant comme score la valeur de la dernière case remplie, même tout de
même à un résultat correct en ce qui concerne les grilles maximales.

Algorithme
----------

Étude de l'espace des solutions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Une approche naïve pour résoudre ce problème est de tester toutes les solutions
possibles : il y a 9 cases possibles au départ, 8 ensuite, 7 ensuite, etc.
Cela fait donc au total :math:`9!` solutions, soit 362880. Ça n'est pas si
grand que ça : mon ordinateur, qui est loin d'être une bête de course, devrait
pouvoir tester tout cela en moins d'une minute, mais nous allons pouvoir
améliorer cela.

En énumérant toutes les solutions possibles, certaines solutions sont étudiées
plusieurs fois. Par exemple, considérons les débuts de solutions suivantes (où
les numéros indiquent l'ordre de remplissage).

+----------------------------+----------------------------+----------------------------+----------------------------+
| .. math::                  | .. math::                  | .. math::                  | .. math::                  |
|     :nowrap:               |     :nowrap:               |     :nowrap:               |     :nowrap:               |
|                            |                            |                            |                            |
|     \begin{array}{|c|c|c|} |     \begin{array}{|c|c|c|} |     \begin{array}{|c|c|c|} |     \begin{array}{|c|c|c|} |
|         \hline             |         \hline             |         \hline             |         \hline             |
|         1  &  3 &   \\     |         1  &    & ~~\\     |            &    & ~~\\     |         ~~ & 3  & 1 \\     |
|         \hline             |         \hline             |         \hline             |         \hline             |
|            &  2 & ~~\\     |         3  & 2  &   \\     |         3  & 2  &   \\     |            & 2  &   \\     |
|         \hline             |         \hline             |         \hline             |         \hline             |
|            &    &   \\     |            &    &   \\     |         1  &    &   \\     |            &    &   \\     |
|         \hline             |         \hline             |         \hline             |         \hline             |
|     \end{array}            |     \end{array}            |     \end{array}            |     \end{array}            |
|                            |                            |                            |                            |
| *(1)*                      | *(2)*                      | *(3)*                      | *(4)*                      |
|                            |                            |                            |                            |
+----------------------------+----------------------------+----------------------------+----------------------------+

* La seconde solution correspond à une symétrie de la première par rapport à la
  diagonale ;
* la troisième à une rotation de la première d'angle :math:`\frac{\pi}{2}` ;
* la quatrième à une symétrie de la première par rapport à une droite
  verticale ;
* et d'autres transformations sont encore possibles.

Finalement, ces quatre solutions (et les autres, non décrites ici) sont
redondantes, et c'est une perte de temps que de toutes les étudier.

Réduction de l'espace
^^^^^^^^^^^^^^^^^^^^^

Il y a :math:`9!` solutions possibles. Pour chacune de ces solutions, il y a
les transformations suivantes, qui donnent une solution équivalente.

    - l'identité (ne rien changer) ;
    - symétrie par une des deux diagonales ;
    - rotation de plus ou moins :math:`\frac{\pi}{2}` (un quart de tour à
      droite ou à gauche) ;
    - symétrie centrale (qui peut être vue comme une rotation de
      :math:`\pi`, ou encore d'un demi tour) ;
    - symétrie par un axe horizontal ou vertical passant par le centre.

Cela fait 8 solutions équivalents et différentes pour chaque solution possible,
soit un nombre de solutions *intéressantes* de :math:`\frac{9!}{8}=45360`.

En ignorant ces solutions équivalentes, nous pouvons donc nous contenter de
recherche parmi huit fois moins de solutions.


Mise en œuvre algorithmique
^^^^^^^^^^^^^^^^^^^^^^^^^^^

On définit une classe :class:`chemin.Solution`, et on s'intéresse ici à la
méthode :meth:`chemin.Solution.solve` et l'attribut
:attr:`chemin.Solution.classes` :

    - :attr:`chemin.Solution.classes` est un dictonnaire dont les clefs sont
      les indices des cases, et les valeurs sont les classes de solution à
      laquelle va appartenir l'objet une fois que ladite case aura été
      complétée.
    - :meth:`chemin.Solution.solve` est une méthode qui recherche toutes les
      solutions possibles à partir de la solution courante, en utilisant
      :attr:`chemin.Solution.classes`.

        .. literalinclude:: ../jouets/chemin/__init__.py
            :linenos:
            :pyobject: Solution.solve

Des sous-classes particulières font varier l'attribut
:attr:`chemin.Solution.classes`.

Par exemple, la classe :class:`SolutionVide` représente une solution qui n'a
pas encore été complétée. Les cases qu'il est utile de compléter sont la case
centrale, la case supérieure gauche, et la case en bas au milieu. Les autres
cases mèneront à des solutions identiques à transformation près.

.. literalinclude:: ../jouets/chemin/__init__.py
    :linenos:
    :pyobject: SolutionVide

De même, à partir d'une :class:`SolutionCentrale`, qui représente une solution
dont seule la case centrale est remplie, on peut remplir les cases supérieure
gauche et médiane basse, pour les même raisons que précédemment.

.. literalinclude:: ../jouets/chemin/__init__.py
    :linenos:
    :pyobject: SolutionCentrale


L'exécution de ce programme donne un score maximal de 57, et quatre solutions
qui donnent ce score.

Amélioration possible
---------------------

Parmi les solutions optimales trouvées, on trouve les deux suivante (l'ordre de
remplissage est donné à droite, et la grille correspondante à gauche).

- Solution 1 ::

    1 | 57 | 27       0 | 8 | 7
    2 |  7 | 20       2 | 4 | 6
    1 |  3 | 10       1 | 3 | 5

- Solution 2 ::

    1 |  3 | 10       0 | 3 | 5
    2 |  7 | 20       2 | 4 | 6
    1 | 57 | 27       1 | 8 | 7

Ces deux solutions apparaissent comme le symétrique l'une de l'autre par un axe
horizontal médian. Pourquoi notre algorithme donne-t-il les deux solutions ?

C'est parce que si on regarde l'ordre de remplissage, on s'aperçoit que ce sont
bien deux solutions différentes : les deux cases prenant la valeur `1` ne sont
pas remplies dans le même ordre, même si le résultat final est similaire.

Une amélioration possible de notre algorithme serait de prendre en compte ce
genre de similarités, pour étudier encore moins de solutions.

Pour aller plus loin
====================

Cet exercice est plutôt simple, et l'espace des solutions (composé de 362880
éléments), n'est finalement pas si grand que ça pour nos ordinateurs
contemporains. Ces optimisations n'étaient donc pas forcément nécessaires.

Il serait intéressant de se demander dans quelle mesure il peut être adapté à
un problème plus gros, comme la résolution d'une partie de `solitaire
<http://fr.wikipedia.org/wiki/Solitaire_(casse-tête)>`_. De remarques me
viennent alors.

    - Dans cet algorithme, il n'est jamais nécessaire de deviner dans quelle
      configuration on se trouve (grille vide, seule une diagonale remplie,
      seul le centre rempli, etc.). Ceci a pu être fait car l'espace des
      solutions étant petit, il était plus simple de coder cela *à la main*
      dans les attributs :attr:`Solution.classes` plutôt que de le recalculer.
      Pour un solitaire, je pense qu'il serait nécessaire de faire le calcul.
    - L'amélioration évoquée dans la partie précédante devra peut-être être
      prise en compte.

Enfin, il est également possible que ma méthode ne s'applique pas à des
problèmes plus gros… Mais je n'en ai aucune idée…
