.. _dobble_math:

********************
Analyse mathématique
********************

La première partie (:ref:`dobble_math_definitions`) propose quelques
définitions nécessaires à la lecture de la suite. Les deux parties suivantes
sont indépendantes : :ref:`dobble_math_combinatoire` décrit quelques propriétés
des configurations de Dobble, mais ces propriétés ne sont pas utilisées dans la
partie :ref:`dobble_math_algorithme`, qui donne l'algorithme utilié pour
générer des jeux de tailles arbitrairement grandes. La dernière partie
(:ref:`dobble_math_bilan`), enfin, dresse un bilan de cette analyse.

.. contents::
  :depth: 1
  :local:

.. _dobble_math_definitions:

Définitions
===========

Commençons par donner quelques définitions.

.. proof:definition:: Objets de base

    * On se munit d'un ensemble infini d'éléments, appelés *symboles*.
    * Une *carte* est un ensemble de symboles.
    * Une *configuration* est un ensemble de cartes.

.. proof:definition:: Caractéristiques des configurations

    Une configuration est dite :

    * *valide* si :

        * tout couple de cartes a un et un seul symbole en commun ;
        * deux symboles quelconques apparaissent exactement une fois sur une
          même carte.

    * *triviale* si elle est constituée de cartes identiques ne contenant qu'un
      seul symbole (notons qu'une telle configuration est valide, mais peu
      intéressante pour jouer) ;
    * *régulière* si :

        * chaque symbole apparait autant de fois dans le jeu ;
        * toutes les cartes possèdent le même nombre de symboles.

Les configurations régulières sont intéressantes car il n'est pas possible
d'ajouter une carte, et d'obtenir une configuration valide, sans ajouter un
nouveau symbole.

Nous pouvons déjà remarquer qu'il est pertinent de s'intéresser aux
configurations *valides*, *triviales* et *régulières*, puisques de telles
configurations existent. En voici des exemples (les cadres correspondent aux
cartes, et les chiffres sont les symboles).

+----------------------------------------------------------+----------------------------------------------------+---------------------------------------------------+
| .. tikz:: Configuration valide régulière                 |                                                    | .. tikz:: Configuration non-valide                |
|                                                          | .. tikz:: Configuration valide non-régulière       |                                                   |
|     \draw (0,.5) node[carte]{\begin{tikzpicture}         |                                                    |     \draw (0,1) node[carte]{\begin{tikzpicture}   |
|         \node[symbole, left ] {1};                       |     \draw (0,1) node[carte]{\begin{tikzpicture}    |         \node[symbole, left ] {1};                |
|         \node[symbole, right] {2};                       |         \node[symbole, left ] {1};                 |         \node[symbole, right] {2};                |
|         \end{tikzpicture}};                              |         \node[symbole, right] {2};                 |         \end{tikzpicture}};                       |
|     \draw (0,-.5) node[carte] {\begin{tikzpicture}       |         \end{tikzpicture}};                        |     \draw (0,-1) node[carte] {\begin{tikzpicture} |
|         \node[symbole, left ] {2};                       |     \draw (0,-1) node[carte] {\begin{tikzpicture}  |         \node[symbole, left ] {2};                |
|         \node[symbole, right] {3};                       |         \node[symbole, left ] {2};                 |         \node[symbole, right] {3};                |
|         \end{tikzpicture}};                              |         \node[symbole, right] {3};                 |         \end{tikzpicture}};                       |
|     \draw ({sqrt(3)},0) node[carte]{\begin{tikzpicture}  |         \node[symbole, below] {4};                 |     \draw (1,0) node[carte]{\begin{tikzpicture}   |
|         \node[symbole, left ] {1};                       |         \end{tikzpicture}};                        |         \node[symbole, above] {1};                |
|         \node[symbole, right] {3};                       |     \draw (1,0) node[carte]{\begin{tikzpicture}    |         \node[symbole, below] {3};                |
|         \end{tikzpicture}};                              |         \node[symbole, above] {1};                 |         \end{tikzpicture}};                       |
|                                                          |         \node[symbole, below] {3};                 |     \draw (-1,0) node[carte]{\begin{tikzpicture}  |
|                                                          |         \end{tikzpicture}};                        |         \node[symbole, above] {1};                |
|                                                          |     \draw (-1,0) node[carte]{\begin{tikzpicture}   |         \node[symbole, below] {4};                |
|                                                          |         \node[symbole, above] {1};                 |         \end{tikzpicture}};                       |
|                                                          |         \node[symbole, below] {4};                 |                                                   |
|                                                          |         \end{tikzpicture}};                        |                                                   |
+----------------------------------------------------------+----------------------------------------------------+---------------------------------------------------+


.. _dobble_math_combinatoire:

Combinatoire
============

Propriétés des configurations régulières
----------------------------------------

Notons quelques propriétés intéressantes concernant les configurations
régulières.  Ces propriétés ne seront pas utilisées dans notre algorithme, mais
elles éclairent l'ensemble des configurations régulières.

.. proof:definition::

    Étant donné une configuration, on nomme :

    * :math:`a` le nombre d'apparition de chaque symbole ;
    * :math:`c` le nombre de cartes ;
    * :math:`s` le nombre de symboles différents ;
    * :math:`n` le nombre de symboles par carte.

.. proof:example:: Configuration régulière

    .. tikz::

        % Symboles
        \draw (0,0) node[carte](c0){\begin{tikzpicture}
            \node[left,symbole,red] (s01){$1$};
            \node[right,symbole,green](s02){$2$};
            \node[      symbole,lightgray](s07){$7$};
        \end{tikzpicture}};
        \draw (0:2) node[carte](c1){\begin{tikzpicture}
            \node[left,symbole,blue](s13){$3$};
            \node[      symbole,orange](s15){$5$};
            \node[right,symbole,red](s11){$1$};
        \end{tikzpicture}};
        \draw (60:2) node[carte](c2){\begin{tikzpicture}
            \node[left,symbole,olive](s24){$4$};
            \node[      symbole,purple](s26){$6$};
            \node[right,symbole,red](s21){$1$};
        \end{tikzpicture}};
        \draw (120:2) node[carte](c3){\begin{tikzpicture}
            \node[left,symbole,olive](s34){$4$};
            \node[      symbole,orange](s35){$5$};
            \node[right,symbole,green](s32){$2$};
        \end{tikzpicture}};
        \draw (180:2) node[carte](c4){\begin{tikzpicture}
            \node[left,symbole,blue](s43){$3$};
            \node[      symbole,purple](s46){$6$};
            \node[right,symbole,green](s42){$2$};
        \end{tikzpicture}};
        \draw (240:2) node[carte](c5){\begin{tikzpicture}
            \node[left,symbole,orange](s55){$5$};
            \node[      symbole,purple](s56){$6$};
            \node[right,symbole,lightgray](s57){$7$};
        \end{tikzpicture}};
        \draw (300:2) node[carte](c6){\begin{tikzpicture}
            \node[left,symbole,blue](s63){$3$};
            \node[      symbole,olive](s64){$4$};
            \node[right,symbole,lightgray](s67){$7$};
        \end{tikzpicture}};

        % Relations
        \draw[relation,red   ] (c0) to[] (c1) to[] (c2) to[] (c0);
        \draw[relation,green ] (c0) to[] (c3) to[] (c4) to[] (c0);
        \draw[relation,blue  ] (c1) to[bend right] (c4);
        \draw[relation,blue  ] (c4) to[] (c6) to[] (c1);
        \draw[relation,olive] (c6) to[] (c2) to[] (c3);
        \draw[relation,olive] (c3) to[bend right] (c6);
        \draw[relation,orange] (c1) to[] (c3) to[] (c5) to[] (c1);
        \draw[relation,purple] (c2) to[] (c4) to[] (c5);
        \draw[relation,purple] (c5) to[bend right] (c2);
        \draw[relation,lightgray  ] (c0) to[] (c5) to[] (c6) to[] (c0);

    La configuration ci-dessus possède 7 cartes (:math:`c=7`) comportant 3
    symboles chacune (:math:`n=3`), chaque symbole apparaissant 3 fois
    (:math:`a=3`), pour un total de 7 symboles différents (:math:`s=7`).

.. proof:property::

    Pour toute configuration régulière, on a la relation :math:`sa(a-1)=c(c-1)`.

.. proof:proof::

    C'est un type de raisonnement classique en combinatoire : compter de deux
    manières différentes le même ensemble d'objets. Ici, nous comptons le
    nombre de relations entre les symboles.

    On appelle relation entre deux symboles un couple de symboles identiques
    (qui peut être matérialisé par un segment reliant ces deux symboles), et on
    compte le nombre de ces relations.

    D'une part, chaque symbole est en lien avec :math:`a-1` autres symboles,
    donc pour un type de symbole donné, il y a :math:`\frac{a(a-1)}{2}`
    relations. Multiplié par le nombre de symboles différents :math:`s`, cela
    donne :math:`\frac{sa(a-1)}{2}`.

    D'autre part, puisque que pour tout couple de carte, il y a un et un seul
    symbole en commun, cela signifie qu'il y a exactement une relation entre
    deux cartes quelconques (et aucune relations à l'intérieur d'une carte).
    Donc le nombre de relations est égal aux nombre de couples de cartes, soit
    :math:`\frac{c(c-1)}{2}`.

    Ainsi :

    .. math::

        \frac{sa(a-1)}{2} &= \frac{c(c-1)}{2} \\
        sa(a-1) &= c(c-1)


Cette relation donne quelques informations concernant les configurations
régulières. Par exemple, le nombre de symboles différents doit être un diviseur
du produit :math:`c(c-1)` (donc il n'existe pas de configuration régulière à 4
symboles et 6 cartes). Ou encore, une configuration régulière ayant autant de
symboles différents que de cartes est forcément triviale.

.. proof:property::

    Pour toute configuration régulière, on a :math:`nc=as`.

.. proof:proof::

    Comptons, de deux manières différentes, le nombre total de symboles de
    notre jeu.

    D'une part, il y a :math:`c` cartes comportant chacune :math:`n` symboles,
    donc il y a au total :math:`nc` symboles.

    D'autre part, il y a :math:`s` symboles différents, apparaissant chacun
    :math:`a` fois, ce qui fait un total de :math:`as` symboles.

    Donc :math:`nc=as`.

Encore une fois, cela nous donne des informations de divisabilité : par
exemple, le nombre de cartes doit diviser le produit :math:`as`.

.. proof:property::

    Pour toute configuration régulière, on a :math:`cn(n-1)=s(s-1)`.

.. proof:proof::

    Comptons le nombre de couples de symboles sur la même carte.

    D'une part, chaque carte possède :math:`n` symboles, donc
    :math:`\frac{n(n-1)}{2}` couples de symboles. Multiplié par :math:`c`
    cartes, cela fait :math:`\frac{cn(n-1)}{2}`.

    D'autre part, puisque chaque couple de symbole apparait sur une unique
    carte, le nombre de couples de symboles sur la même carte est égal au
    nombre de couples de symboles différents possibles, soit
    :math:`\frac{s(s-1)}{2}`.

    Donc : :math:`\frac{s(s-1)}{2}=\frac{cn(n-1)}{2}`, et donc
    :math:`s(s-1)=cn(n-1)`.

.. proof:property::

    Pour toute configuration régulière, on a :math:`n(a-1)=c-1`.

.. proof:proof::

    Cette propriété se déduit soit des précédentes, soit en comptant de
    deux manières différentes le nombre de relations partant d'une unique
    carte.

.. proof:property::

    Pour toute configuration régulière, on a : :math:`a(n-1)=s-1`.

.. proof:proof::

    C'est une conséquence des égalités :math:`cn(n-1)=s(s-1)` et :math:`cn=as`.

.. proof:property::

    Pour toute configuration régulière, on a : :math:`c+n=s+a`.

.. proof:proof::

    C'est une conséquence des égalités :math:`n(a-1)=c-1` et :math:`a(n-1)=s-1`.

.. proof:property:: Bilan

    Pour toute configuration régulière, on a :

    .. math::

        sa(a-1) &= c(c-1) \\
        cn(n-1) &= s(s-1) \\
        n(a-1) &= c-1 \\
        a(n-1) &= s-1 \\
        nc &= as \\
        c+n &= s+a \\

.. proof:property:: Généralisation aux configurations valides

    Ces propriétés sont des cas particuliers pour les configurations régulières
    des relations suivantes, valables pour n'importe quelle configuration
    valide.

    Pour une configuration quelconque, on note :

    * :math:`S` l'ensemble des symboles ;
    * :math:`C` l'ensemble des cartes ;
    * :math:`s=\operatorname{card}(S)` le nombre de symboles différents ;
    * :math:`c=\operatorname{card}(C)` le nombre de cartes ;
    * :math:`a_i=\operatorname{card}\left\{j\in C|i\in j\right\}` (pour :math:`i\in S`) le nombre d'apparition du symbole :math:`i` ;
    * :math:`n_j=\operatorname{card}(j)` (pour :math:`j\in C`) le nombre de symboles sur la carte :math:`j`.

    Pour toute configuration valide, on a alors les relations suivantes :

    .. math::

        \sum_{i\in S}a_i(a_i-1) &= c(c-1) \\
        \sum_{j\in C}n_j(n_j-1) &= s(s-1) \\
        \forall i\in S, \sum_{i\in j\in C} n_j &= s+a_i-1\\
        \forall j\in C, \sum_{i\in j} a_i &= c+n_j-1\\
        \sum_{i\in S}a_i &= \sum_{j\in C}n_j \\

.. proof:proof::

    - :math:`\sum\limits_{i\in S}a_i(a_i-1) = c(c-1)` est obtenu en comptant le
      nombre de couples de symboles identiques.

    - :math:`\sum\limits_{j\in C}n_j(n_j-1) = s(s-1)` est obtenu en comptant le nombre
      de couples de symboles différents sur la même carte.

    - :math:`\forall i\in S, \sum\limits_{i\in j\in C} n_j = s+a_i-1` est obtenu, pour
      un symbole :math:`i` quelconque, en calculant la somme des tailles des
      cartes contenant ce même symbole.

    - :math:`\forall j\in C, \sum\limits_{i\in j} a_i = c+n_j-1` est obtenu, pour une
      carte :math:`j` quelconque, en calculant le nombre d'apparition de
      l'ensemble des symboles de cette carte.

    - :math:`\sum\limits_{i\in S}a_i = \sum\limits_{j\in C}n_j` est obtenu en comptant le
      nombre total de symboles (incluant les répétitions).


Configurations duales
---------------------

.. proof:definition:: Configuration duale

    Étant donnée une configuration :math:`\Delta`, constituée des
    cartes :math:`C`, elles-mêmes constituées d'éléments de l'ensemble de
    symboles :math:`S`, on appelle *dual* de :math:`\Delta`, noté
    :math:`\Delta^*`, la configuration :

    * construite avec des symboles :math:`C` ;
    * constituée des cartes :math:`\left\{c\in C|s\in c\right\}`, pour
      :math:`s\in S`.

    En d'autres termes :

    * les cartes :math:`C` de la configuration :math:`\Delta` forment les
      symboles :math:`S^*` de la configuration duale :math:`\Delta^*` ;
    * pour chaque symbole de :math:`\Delta`, l'ensemble des cartes de
      :math:`\Delta` contenant ce symbole constitue une carte de
      :math:`\Delta^*`.

.. proof:example:: Dual d'une configuration régulière

    +---------------------------------------------------------------------+---------------------------------------------------------+
    |                                                                     |                                                         |
    | .. tikz:: Dual d'une configuration régulière                        |  .. tikz:: Configuration d'origine                      |
    |                                                                     |                                                         |
    |     % Symboles                                                      |      % Symboles                                         |
    |     \draw (0,0) node[dcarte,red,thick]{\begin{tikzpicture}          |      \draw (0,0) node[carte](c0){\begin{tikzpicture}    |
    |         \draw (0:.7) node[carte](c0){\begin{tikzpicture}            |          \node[left,symbole,red] (s01){$1$};            |
    |             \node[left,symbole,red] (s01){$1$};                     |          \node[right,symbole,green](s02){$2$};          |
    |             \node[right,symbole,green](s02){$2$};                   |          \node[      symbole,lightgray](s07){$7$};      |
    |             \node[      symbole,lightgray](s07){$7$};               |      \end{tikzpicture}};                                |
    |         \end{tikzpicture}};                                         |      \draw (0:2) node[carte](c1){\begin{tikzpicture}    |
    |         \draw (120:.7) node[carte](c1){\begin{tikzpicture}          |          \node[left,symbole,blue](s13){$3$};            |
    |             \node[left,symbole,blue](s13){$3$};                     |          \node[      symbole,orange](s15){$5$};         |
    |             \node[      symbole,orange](s15){$5$};                  |          \node[right,symbole,red](s11){$1$};            |
    |             \node[right,symbole,red](s11){$1$};                     |      \end{tikzpicture}};                                |
    |         \end{tikzpicture}};                                         |      \draw (60:2) node[carte](c2){\begin{tikzpicture}   |
    |         \draw (240:.7) node[carte](c2){\begin{tikzpicture}          |          \node[left,symbole,olive](s24){$4$};           |
    |             \node[left,symbole,olive](s24){$4$};                    |          \node[      symbole,purple](s26){$6$};         |
    |             \node[      symbole,purple](s26){$6$};                  |          \node[right,symbole,red](s21){$1$};            |
    |             \node[right,symbole,red](s21){$1$};                     |      \end{tikzpicture}};                                |
    |         \end{tikzpicture}};                                         |      \draw (120:2) node[carte](c3){\begin{tikzpicture}  |
    |     \end{tikzpicture}};                                             |          \node[left,symbole,olive](s34){$4$};           |
    |                                                                     |          \node[      symbole,orange](s35){$5$};         |
    |     \draw (0:4) node[dcarte,green,thick]{\begin{tikzpicture}        |          \node[right,symbole,green](s32){$2$};          |
    |         \draw (0:.7) node[carte](c0){\begin{tikzpicture}            |      \end{tikzpicture}};                                |
    |             \node[left,symbole,red] (s01){$1$};                     |      \draw (180:2) node[carte](c4){\begin{tikzpicture}  |
    |             \node[right,symbole,green](s02){$2$};                   |          \node[left,symbole,blue](s43){$3$};            |
    |             \node[      symbole,lightgray](s07){$7$};               |          \node[      symbole,purple](s46){$6$};         |
    |         \end{tikzpicture}};                                         |          \node[right,symbole,green](s42){$2$};          |
    |         \draw (120:.7) node[carte](c3){\begin{tikzpicture}          |      \end{tikzpicture}};                                |
    |             \node[left,symbole,olive](s34){$4$};                    |      \draw (240:2) node[carte](c5){\begin{tikzpicture}  |
    |             \node[      symbole,orange](s35){$5$};                  |          \node[left,symbole,orange](s55){$5$};          |
    |             \node[right,symbole,green](s32){$2$};                   |          \node[      symbole,purple](s56){$6$};         |
    |         \end{tikzpicture}};                                         |          \node[right,symbole,lightgray](s57){$7$};      |
    |         \draw (240:.7) node[carte](c4){\begin{tikzpicture}          |      \end{tikzpicture}};                                |
    |             \node[left,symbole,blue](s43){$3$};                     |      \draw (300:2) node[carte](c6){\begin{tikzpicture}  |
    |             \node[      symbole,purple](s46){$6$};                  |          \node[left,symbole,blue](s63){$3$};            |
    |             \node[right,symbole,green](s42){$2$};                   |          \node[      symbole,olive](s64){$4$};          |
    |         \end{tikzpicture}};                                         |          \node[right,symbole,lightgray](s67){$7$};      |
    |     \end{tikzpicture}};                                             |      \end{tikzpicture}};                                |
    |                                                                     |                                                         |
    |     \draw (60:4) node[dcarte,blue,thick]{\begin{tikzpicture}        |                                                         |
    |         \draw (0:.7) node[carte](c1){\begin{tikzpicture}            |                                                         |
    |             \node[left,symbole,blue](s13){$3$};                     |                                                         |
    |             \node[      symbole,orange](s15){$5$};                  |                                                         |
    |             \node[right,symbole,red](s11){$1$};                     |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (120:.7) node[carte](c4){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,blue](s43){$3$};                     |                                                         |
    |             \node[      symbole,purple](s46){$6$};                  |                                                         |
    |             \node[right,symbole,green](s42){$2$};                   |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (240:.7) node[carte](c6){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,blue](s63){$3$};                     |                                                         |
    |             \node[      symbole,olive](s64){$4$};                   |                                                         |
    |             \node[right,symbole,lightgray](s67){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |     \end{tikzpicture}};                                             |                                                         |
    |                                                                     |                                                         |
    |     \draw (120:4) node[dcarte,olive,thick]{\begin{tikzpicture}      |                                                         |
    |         \draw (0:.7) node[carte](c2){\begin{tikzpicture}            |                                                         |
    |             \node[left,symbole,olive](s24){$4$};                    |                                                         |
    |             \node[      symbole,purple](s26){$6$};                  |                                                         |
    |             \node[right,symbole,red](s21){$1$};                     |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (120:.7) node[carte](c3){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,olive](s34){$4$};                    |                                                         |
    |             \node[      symbole,orange](s35){$5$};                  |                                                         |
    |             \node[right,symbole,green](s32){$2$};                   |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (240:.7) node[carte](c6){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,blue](s63){$3$};                     |                                                         |
    |             \node[      symbole,olive](s64){$4$};                   |                                                         |
    |             \node[right,symbole,lightgray](s67){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |     \end{tikzpicture}};                                             |                                                         |
    |                                                                     |                                                         |
    |     \draw (180:4) node[dcarte,orange,thick]{\begin{tikzpicture}     |                                                         |
    |         \draw (0:.7) node[carte](c1){\begin{tikzpicture}            |                                                         |
    |             \node[left,symbole,blue](s13){$3$};                     |                                                         |
    |             \node[      symbole,orange](s15){$5$};                  |                                                         |
    |             \node[right,symbole,red](s11){$1$};                     |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (120:.7) node[carte](c3){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,olive](s34){$4$};                    |                                                         |
    |             \node[      symbole,orange](s35){$5$};                  |                                                         |
    |             \node[right,symbole,green](s32){$2$};                   |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (240:.7) node[carte](c5){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,orange](s55){$5$};                   |                                                         |
    |             \node[      symbole,purple](s56){$6$};                  |                                                         |
    |             \node[right,symbole,lightgray](s57){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |     \end{tikzpicture}};                                             |                                                         |
    |                                                                     |                                                         |
    |     \draw (240:4) node[dcarte,purple,thick]{\begin{tikzpicture}     |                                                         |
    |         \draw (0:.7) node[carte](c2){\begin{tikzpicture}            |                                                         |
    |             \node[left,symbole,olive](s24){$4$};                    |                                                         |
    |             \node[      symbole,purple](s26){$6$};                  |                                                         |
    |             \node[right,symbole,red](s21){$1$};                     |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (120:.7) node[carte](c4){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,blue](s43){$3$};                     |                                                         |
    |             \node[      symbole,purple](s46){$6$};                  |                                                         |
    |             \node[right,symbole,green](s42){$2$};                   |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (240:.7) node[carte](c5){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,orange](s55){$5$};                   |                                                         |
    |             \node[      symbole,purple](s56){$6$};                  |                                                         |
    |             \node[right,symbole,lightgray](s57){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |     \end{tikzpicture}};                                             |                                                         |
    |                                                                     |                                                         |
    |                                                                     |                                                         |
    |     \draw (300:4) node[dcarte,lightgray,thick]{\begin{tikzpicture}  |                                                         |
    |         \draw (0:.7) node[carte](c0){\begin{tikzpicture}            |                                                         |
    |             \node[left,symbole,red] (s01){$1$};                     |                                                         |
    |             \node[right,symbole,green](s02){$2$};                   |                                                         |
    |             \node[      symbole,lightgray](s07){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (120:.7) node[carte](c5){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,orange](s55){$5$};                   |                                                         |
    |             \node[      symbole,purple](s56){$6$};                  |                                                         |
    |             \node[right,symbole,lightgray](s57){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |         \draw (240:.7) node[carte](c6){\begin{tikzpicture}          |                                                         |
    |             \node[left,symbole,blue](s63){$3$};                     |                                                         |
    |             \node[      symbole,olive](s64){$4$};                   |                                                         |
    |             \node[right,symbole,lightgray](s67){$7$};               |                                                         |
    |         \end{tikzpicture}};                                         |                                                         |
    |     \end{tikzpicture}};                                             |                                                         |
    |                                                                     |                                                         |
    +---------------------------------------------------------------------+---------------------------------------------------------+

.. proof:property:: Dual d'un dual

    Pour toute configuration :math:`\Delta`, en identifiant les cartes de
    :math:`\Delta` aux symboles correspondants, on a :
    :math:`\Delta^{**}=\Delta`.

    En d'autres termes : le dual du dual d'une configuration est égal à la
    configuration elle-même.

.. proof:proof::

    La démonstration est laissée au lecteur patient.

.. proof:property::

    Le dual d'une configuration :math:`\Delta` est valide (respectivement
    régulière) si et seulement si :math:`\Delta` est valide (respectivement
    régulière).

.. proof:proof::

    Soit :math:`\Delta` une configuration, constituée de l'ensemble de cartes
    :math:`C` et des symboles :math:`S`.

    * Validité

        Le fait que deux cartes de :math:`\Delta^*` aient exactement un seul
        symbole commun se traduit par :
        :math:`\forall \left(c_1^*, c_2^*\right)\in {C^*}^2 , \operatorname{card}\left(c_1^*\cap c_2^*\right) = 1`.

        Or à :math:`c_1^*` et :math:`c_2^*` correspondent deux symboles
        :math:`s_1` et :math:`s_2` de :math:`\Delta` (où :math:`c_1^*` (resp.
        :math:`c_2`) est l'ensemble des cartes de :math:`\Delta` contenant
        :math:`s_1` (resp.  :math:`s_2`)). Donc :

        .. math::

            c_1^* &= \left\{c\in C|s_1\in c\right\} \\
            c_2^* &= \left\{c\in C|s_2\in c\right\} \\

        Et donc :math:`c_1^*\cap c_2^*=\left\{c\in C|s_1\in c \text{ et }s_2\in c\right\}`.

        Ainsi, le fait que deux cartes de :math:`\Delta^*` aient ayactement un seul symbole commun se traduit par :
        :math:`\forall \left(s_1, s_2\right)\in S^2, \operatorname{card}\left\{c\in C|s_1\in c \text{ et } s_2\in c\right\}=1`.
        En d'autres termes, pour tout couple de symboles de :math:`\Delta`, il
        existe une unique carte les contenant tous les deux.

        Nous avons montré que la propriété « Tout couple de cartes de
        :math:`\Delta^*` ont exactement un symbole commun » est équivalent à
        « Tout couple de symboles de :math:`\Delta` est présent ensemble dans
        une unique carte ».

        De même, la propriété « Tout couple de cartes de :math:`\Delta` ont
        exactement un symbole commun » est équivalent à « Tout couple de
        symboles de :math:`\Delta^*` est présent ensemble dans une unique
        carte ». Cela se prouve soit par un argument similaire au précédent,
        soit en utilisant le fait que :math:`\Delta^{**}=\Delta`.

        Ainsi, :math:`\Delta` est valide si et seulement si :math:`\Delta^*`.

    * Régularité

        Nous supposons maintenant :math:`\Delta` valide.

        Puisqu'il y a correspondance entre les cartes de :math:`\Delta` et les
        symboles de :math:`\Delta^*`, et entre les cartes de :math:`\Delta^*`
        et les symboles de :math:`\Delta`, on a :

        * chaque symbole de :math:`\Delta` apparait autant de fois si et
          seulement si les cartes de :math:`\Delta^*` possèdent le même nombre
          de symboles ;
        * les cartes de :math:`\Delta` possèdent le même nombre de symboles si
          et seulement si chaque symbole de :math:`\Delta^*` apparait autant de
          fois.

        En d'autres termes, :math:`\Delta` étant valide, :math:`\Delta` est
        régulière si et seulement si :math:`\Delta^*` est régulière.

Ce lien entre une configuration et son dual n'est pas surprenant si l'on fait,
comme Bourrigan, le lien avec la géométrie projective. En effet, Bourrigan voit
les configurations valides comme des configurations géométriques, où les
symboles sont des droites (ou des cercles), et les cartes des intersections de
droites (ou cercles). Or, en géométrie projective, dans une certaine mesure,
étant donné une propriété, une propriété analogue existe en considérant des
droites et cercles à la place des points, et des points à la place des droites
et cercle (voir par exemple `l'article de Wikipédia correspondant
<http://fr.wikipedia.org/wiki/Dualit%C3%A9_%28g%C3%A9om%C3%A9trie_projective%29>`_).

Je m'y connais peu en géométrie projective, mais je pense que la notion de
dualité des configurations que nous développons ici est équivalente à la notion
de dualité des configurations vue comme des figures de géométrie projective.

Une dernière remarque à propos de cette dualité est que :

    - le nombre de cartes d'une configuration est égal au nombre de symboles de
      son dual (et inversement) ;
    - le nombre d'apparitions d'un symbole d'une configuration est égal au
      nombre de symboles de la carte correspondante dans le dual (et
      inversement).

Ainsi, avec cette correspondance, on peut voir dans les relations entre les
coefficients démontrées précédemment plusieurs couples de propriétés duales.

.. proof:property:: Correspondance entre les propriétés

    Pour toute configuration régulière, on a :

    .. math::

        \begin{array}{c|c}
            \text{Propriété} & \text{Propriété duale} \\
            \hline
            sa(a-1) = c(c-1) & cn(n-1) = s(s-1) \\
            n(a-1) = c-1 & a(n-1) = s-1 \\
            nc = as & nc = as \\
            c+n = s+a & c+n = s+a \\
        \end{array}


.. _dobble_math_algorithme:

Algorithme
==========

Voici l'algorithme pour générer une configuration régulière, en fonction d'un
nombre premier :math:`p` (le fait que ce nombre *doit* être premier sera prouvé
par la suite).

Exemple
-------

L'exemple suivant est détaillé sous le graphique.

    .. tikz::

        [scale=0.5]
        \foreach \step in {1, ..., 6} {
            \begin{scope}[xshift={450*int((\step-1)/3)}, yshift={-170*mod(\step-1,3)}]
                \draw (0,4) node{Étape \step};
                % Cartes, et tas : 0 1 2
                \foreach \x in {0, ..., 2} {
                    \foreach \y in {0, ..., 2} {
                        \draw ({4*\x+\y},3) node[symbole]{\x};
                        \draw[rounded corners=2pt] ({4*\x+\y-.4},{0-.4}) -- ++(.8, 0) -- ++(0,{3+.8}) -- ++(-.8,0) -- cycle;
                    }
                }

                % Tas : a b c
                \ifnum\step>1 {
                    \foreach \x in {0, ..., 2} {
                        \draw ({0+4*\x},0) node[symbole]{a};
                        \draw ({1+4*\x},0) node[symbole]{b};
                        \draw ({2+4*\x},0) node[symbole]{c};
                    }
                }\fi

                % Tas : u v w
                \ifnum\step>2 {
                    \draw (0,1) node[symbole]{u};
                    \draw (1,1) node[symbole]{v};
                    \draw (2,1) node[symbole]{w};
                    \draw (4,1) node[symbole]{w};
                    \draw (5,1) node[symbole]{u};
                    \draw (6,1) node[symbole]{v};
                    \draw (8,1) node[symbole]{v};
                    \draw (9,1) node[symbole]{w};
                    \draw (10,1) node[symbole]{u};
                }\fi

                \ifnum\step>3 {
                    % Tas : r s t
                    \draw (0,2) node[symbole]{r};
                    \draw (1,2) node[symbole]{s};
                    \draw (2,2) node[symbole]{t};
                    \draw (4,2) node[symbole]{s};
                    \draw (5,2) node[symbole]{t};
                    \draw (6,2) node[symbole]{r};
                    \draw (8,2) node[symbole]{t};
                    \draw (9,2) node[symbole]{r};
                    \draw (10,2) node[symbole]{s};
                }\fi

                \ifnum\step>4 {
                    % Familles
                    \foreach \i in {0, ..., 3} {
                        \draw[rounded corners=2pt] ({13-.4},{\i-.4}) -- ({16+.4},{\i-.4}) -- ({16+.4},{\i+.4}) -- ({13-.4},{\i+.4}) -- cycle;
                    }
                    \draw (13,3) node[symbole]{0};
                    \draw (14,3) node[symbole]{1};
                    \draw (15,3) node[symbole]{2};
                    \draw (13,0) node[symbole]{a};
                    \draw (14,0) node[symbole]{b};
                    \draw (15,0) node[symbole]{c};
                    \draw (13,1) node[symbole]{u};
                    \draw (14,1) node[symbole]{v};
                    \draw (15,1) node[symbole]{w};
                    \draw (13,2) node[symbole]{r};
                    \draw (14,2) node[symbole]{s};
                    \draw (15,2) node[symbole]{t};
                }\fi

                \ifnum\step>5 {
                    % Dernier
                    \foreach \i in {0, ..., 3} {
                        \draw (16,\i) node[symbole]{$\alpha$};
                    }
                }\fi
            \end{scope}
        }

.. hlist::

    * *Préparation* On se donne :math:`p` familles de :math:`p` symboles, et un
      symbole supplémentaire. On commence par faire :math:`p` tas de :math:`p`
      cartes.
    * *Étape 1* Chaque carte d'un même tas reçois un même symbole d'une
      première famille (1, 2 et 3 dans notre cas).
    * *Étape 2* Les cartes du premier tas reçoivent trois symboles :math:`a`,
      :math:`b` et :math:`c`, et les cartes des tas suivants reçoivent les
      symboles de la même famille.
    * *Étape 3* Les cartes reçoivent un symbole chacune, suivant la même
      logique qu'à l'étape précédente, excepté que les symboles des tas
      suivants sont décalés d'un symbole (le premier symbole apparait sur la
      carte 1 du tas 1, sur la carte 2 du tas 2, et ainsi de suite ; le second
      symbole apparait sur la carte 2 du tas 1, 3 du tas 2, et 1 du tas 3).
    * *Étape 4* C'est la même étape que la précédente, avec un décalage de deux
      cartes : le symbole 1 apparait sur la carte 1 du tas 1, la carte 3 du tas
      2, et la carte 2 du tas 3.
    * *Étape 5* À ce stade, nous avons des cartes qui forment une configuration
      valide. Cette configuration n'est toutefois pas régulière. Notamment, les
      symboles d'une famille ne se retrouvent jamais sur la même carte (alors
      que chaque couple de symboles devrait apparaitre sur une unique carte).
      Pour résoudre ce problème, nous créons une carte par famille de symboles,
      contenant tous les symboles de ladite famille.
    * *Étape 6* Les cartes nouvellement ajoutées n'ont pas de symboles communs.
      Nous ajoutons donc un dernier symbole qui les lie.

Prérequis
---------

Le seul prérequis, outre de l'arithmétique de base, et une certaine aisance
avec la lecture de symboles mathématiques, est une connaissance des anneaux
:math:`\mathbb{Z}/n\mathbb{Z}`.

Pour un certain entier :math:`n`, lorsqu'on fait des calculs dans l'anneau
:math:`\mathbb{Z}/n\mathbb{Z}`, les calculs sont faits *modulo* :math:`n`.

Par exemple, dans :math:`\mathbb{Z}/6\mathbb{Z}` :

* :math:`10=6+4=4`
* :math:`7*3=21=6*3+3=3`
* etc.

Description formelle
--------------------

.. proof:definition::

    * Une *famille* de symboles est un ensemble de symboles, d'intersection nulle
      avec chacune des autres familles de symboles.
    * Un *tas* de cartes est un ensemble de cartes, d'intersection nulle avec
      chacun des autres tas de cartes.
    * Un *marqueur de tas* est un symbole, présent sur toutes les cartes d'un
      tas, et uniquement sur celles-ci. En d'autres termes, il caractérise le
      tas.

.. proof:algorithm::

    Dans toute la suite, nous ne manipulons que des nombres entiers, donc les
    intervalles :math:`\left[a, b\right]` désignent les nombres *entiers* entre
    :math:`a` et :math:`b`.

    Commençons par définir les objets que nous allons manipuler.

    * :math:`p` est un entier naturel non nul.
    * On se donne les symboles :math:`d` (le *dernier symbole*), :math:`t_x`,
      pour :math:`x\in \left[0, p-1\right]` (les *marqueurs de tas*), et
      :math:`s_{z,i}`, pour :math:`z` et :math:`i` dans
      :math:`\left[0,p-1\right]`.
    * L'ensemble :math:`\left\{t_x|{x\in\left[0,p-1\right]}\right\}`, et, pour
      tout :math:`z\in\left[0,p-1\right]`, l'ensemble
      :math:`\left\{s_{z,i}|i\in\left[0,p-1\right]\right\}`, sont des *familles
      de symboles*.
    * Chaque :math:`T_{x,y}` (pour :math:`x` et :math:`y` dans
      :math:`\left[0,p-1\right]`) désigne une carte (c'est-à-dire un ensemble de
      symboles), ainsi que chaque :math:`S_x` (pour :math:`x\in\left[0,
      p-1\right]`), et :math:`T`.
    * Chaque :math:`T_x` (pour :math:`x` dans :math:`\left[0,p-1\right]`) est
      un tas contenant l'ensemble de cartes
      :math:`\left\{T_{x,y}|y\in\left[0,p-1\right]\right\}`.
    * Pour :math:`x`, :math:`y`, :math:`z` dans :math:`\left[0,p-1\right]`,
      :math:`T_{x,y}[z]` désigne le symbole de rang :math:`z` de la carte
      :math:`T_{x,y}`.

    L'algorithme est illustré dans la figure suivante, et détaillé en dessous.

    .. tikz::
        :libs: decorations.pathreplacing,calc

        [xscale=1.2,yscale=.5]

        \tikzset{carte/.style={color=blue!50!black}}
        \tikzset{symbole/.style={color=red!50!black}}
        \tikzset{dernier/.style={color=purple!50!black}}
        \tikzset{marqueur/.style={color=green!50!black}}
        \tikzset{generique/.style={color=red,scale=1.5}}
        \tikzset{contourcarte/.style={fill=lightgray!10,rounded corners=2pt}}
        % Contour des cartes
        \foreach \x/\y in {0/-1, 0/1, 2/-2, 2/0, 2/2, 4/-1, 4/1} {
          \begin{scope}[xshift={90*\x}]
            \draw[contourcarte] ({\y-.7}, -.4)
                                    -- ({\y-.7}, {5+.4})
                                    -- ({\y+.7}, {5+.4})
                                    -- ({\y+.7}, -.4)
                                    -- cycle;
          \end{scope}
        }

        % Cartes
        \foreach \x/\index in {0/0, 4/{{p-1}}} {
          \begin{scope}[xshift={90*\x}]
            \node[marqueur] at (-1,5) {$t_\index$};
            \node[carte] (bottomleft) at (-1,-1) {$T_{\index,0}$};
            \node[marqueur] at (1,5) {$t_\index$};
            \node[carte] (bottomright) at (1,-1) {$T_{\index,p-1}$};

            \ifnum\x=0{
              \node[symbole] at (-1,0) {$s_{0,0}$};
              \node[symbole] at (1,0) {$s_{0,p-1}$};
              \node[symbole] at (-1,4) {$s_{{p-1},0}$};
              \node[symbole] at (1,4) {$s_{{p-1},p-1}$};
              \node (tzeroright) at (1,3) {};
            }\fi
            \ifnum\x=4{
              \node[symbole] at (-1,0) {$s_{0,0}$};
              \node[symbole] at (1,0) {$s_{0,p-1}$};
              \node[symbole] at (-1,4) {$s_{{p-1},1}$};
              \node[symbole] at (1,4) {$s_{{p-1},0}$};
              \node (tpleft) at (-1,3) {};
            }\fi
            \node at (0,3) {\Large $\dots$};
            \foreach \i/\j in {-1/2, 1/2} {
              \node[symbole] at (\i,\j) {\Large $\vdots$};
            }
            \draw[carte,decorate,decoration={brace,amplitude=10pt,mirror}] (bottomleft.south west) -- (bottomright.south east) node [midway,below=1em] {$T_{\index}$};
          \end{scope}
        }

        \begin{scope}[xshift={90*2}]
          % Cartes T(x,0) à T(x,p-1)
          \node[marqueur] at (-2,5) {$t_x$};
          \node[carte] (bottomleft) at (-2,-1) {$T_{x,0}$};
          \node[marqueur] at (0,5) {$t_x$};
          \node[carte] at (0,-1) {$T_{x,y}$};
          \node[marqueur] at (2,5) {$t_x$};
          \node[carte] (bottomright) at (2,-1) {$T_{x,p-1}$};
          \node[symbole] at (-2,0) {$s_{0,0}$};
          \node[symbole] at (0,0) {$s_{0,y}$};
          \node[symbole] at (2,0) {$s_{0,p-1}$};
          \node[generique] at (0,2) {$s_{z,xz+y}$};
          \node[symbole] at (-2,4) {$s_{{p-1},p-x}$};
          \node[symbole] at (0,4) {$s_{{p-1},p-x+y}$};
          \node[symbole] at (2,4) {$s_{{p-1},p-x-1}$};
          \foreach \i/\j in {-1/2, 1/2} {
            \node at (\i,\j) {\Large $\dots$};
          }
          \foreach \i/\j in {-2/2, 2/2, 0/1, 0/3} {
            \node[symbole] at (\i,\j) {\Large $\vdots$};
          }
          \node (txleft) at (-2,3) {};
          \node (txright) at (2,3) {};
          \draw[carte,decorate,decoration={brace,amplitude=10pt,mirror}] (bottomleft.south west) -- (bottomright.south east) node [midway,below=1em] {$T_x$};
        \end{scope}

        \node at ($.5*(tpleft)+.5*(txright)$) {\Huge $\ldots$};
        \node at ($.5*(tzeroright)+.5*(txleft)$) {\Huge $\ldots$};

        % Cartes S_0 à S_{p-1}
        \begin{scope}[xshift={95*5}]
          \foreach \z in {0, 4, 5} {
            \draw[contourcarte] ({-1-.5}, {\z-.4})
                                    -- ({-1-.5}, {\z+.4})
                                    -- ({2+.6}, {\z+.4})
                                    -- ({2+.6}, {\z-.4})
                                    -- cycle;
          }
          \draw[draw=none] (-1,5) node[marqueur]{${t_0}$}
                      -- ++(1,0) node[marqueur]{\Large $\dots$}
                      -- ++(1,0) node[marqueur]{$t_{p-1}$}
                      -- ++(1,0) node[dernier]{$d$}
                      -- ++(1,0) node[carte]{$T$};
          \draw[draw=none] (-1,0) node[symbole]{${s_{0,0}}$}
                      -- ++(1,0) node[symbole]{\Large $\dots$}
                      -- ++(1,0) node[symbole]{$s_{0,p-1}$}
                      -- ++(1,0) node[dernier]{$d$}
                      -- ++(1,0) node(Szero)[carte]{$S_0$};
          \draw[draw=none] (-1,4) node[symbole]{${s_{p-1,0}}$}
                      -- ++(1,0) node[symbole]{\Large $\dots$}
                      -- ++(1,0) node[symbole]{$s_{p-1,p-1}$}
                      -- ++(1,0) node[dernier]{$d$}
                      -- ++(1,0) node(Sp)[carte]{$S_{p-1}$};
          \node at (0.5,2) {\Large $\vdots$};
          \draw[carte,decorate,decoration={brace,amplitude=10pt,mirror}] ($(Szero.center)+(.4,0)$) -- ($(Sp.center)+(.4,0)$) node [midway,right=1em] {$S$};
        \end{scope}

    #. Commençons par placer les marqueurs de tas. Pour tous :math:`x` et
       :math:`y` dans :math:`\left[0,p-1\right]`, on a :math:`T{x,y}[p-1]=t_x`.
       Autrement dit : chaque carte d'un tas :math:`T_x` se voit attribuer le
       marqueur de tas :math:`t_x` (et lui seul).
    #. Complétons ensuite les cartes des tas :math:`T_x`. Pour tous :math:`x`,
       :math:`y`, et :math:`z` dans :math:`\left[0, p-1\right]`, on a
       :math:`T_{x,y}[z]=s_{z,xz+y}` (où l'opération :math:`xz+y` est faite
       dans l'anneau :math:`\mathbb{Z}/p\mathbb{Z}`).
    #. La carte :math:`T` reçoit les marqueurs de tas :math:`t_x` (pour
       :math:`x` dans :math:`\left[0,p-1\right]`), ainsi que le dernier symbole
       :math:`d`.
    #. Pour tout :math:`z` dans :math:`\left[0,p-1\right]`, la carte
       :math:`S_z` reçoit les symboles :math:`s_{z,x}`, pour :math:`x` dans
       :math:`\left[0,p-1\right]`, ainsi que le dernier symbole :math:`d`.


Preuve
------

.. proof:theorem::

    Pour un entier :math:`p`, la configuration générée par l'algorithme décrit
    ci-dessus est valide et régulière si et seulement si :math:`p` est premier.

.. proof:proof::

    Quatre propriétés sont à prouver sur cette configuration, pour en faire
    une configuration régulière.

    * Couples de cartes

        Par construction, tout couple de cartes parmi les cartes
        :math:`\left\{S_z|z\in\left[0,p-1\right]\right\}` et :math:`T` ont un
        et un seul symbole commun entre elles.

        De même, chaque couple d'une carte parmi
        :math:`S\cup\left\{T\right\}` et
        une carte parmi les
        :math:`\left(T_{x,y}\right)_{(x,y)\in\left[0,p-1\right]^2}` a un et un
        seul symbole en commun (puisque chaque ligne :math:`z` de la figure
        ne contient que les :math:`p-1` symboles
        :math:`\left(s_{z,i}\right)_{i\in\left[0,p-1\right]}`, eux mêmes
        contenus dans la carte :math:`S_z`, ou, pour la ligne supérieure, que
        les marqueurs de tas
        :math:`\left(t_i\right)_{i\in\left[0,p-1\right]}`, tous contenus dans
        la carte :math:`T`).

        Soient deux cartes d'un même tas :math:`T_x` (où
        :math:`x\in\left[0,p-1\right]`). Par construction, ces cartes n'ont
        que le marqueur de tas :math:`t_x` en commun.

        Restent les couples de cartes de
        :math:`\left(T_{x,y}\right)_{(x,y)\in\left[0,p-1\right]}` appartenant
        à deux tas différents. Soient deux de ces cartes, :math:`T_{x_1,y_1}`
        et :math:`T_{x_2,y_2}`, où :math:`x_1`, :math:`x_2`, :math:`y_1`,
        :math:`y_2` sont des nombres de :math:`\left[0, p-1\right]`, et
        :math:`x_1` et :math:`x_2` sont différents. Ces deux cartes
        contiennent les marqueurs de tas, différents, et respectivement les
        symboles :math:`s_{z_1,x_1z_1+y_1}` et :math:`s_{z_2,x_2z_2+y_2}`,
        pour :math:`z_1` et :math:`z_2` dans :math:`\left[0,p-1\right]`. Si
        :math:`z_2\neq z_2`, alors les deux symboles
        :math:`s_{z_1,x_1z_1+y_1}` et :math:`s_{z_2,x_2z_2+y_2}` sont
        nécessairement différents. Étudions maintenant les symboles
        :math:`s_{z,x_1z+y_1}` et :math:`s_{z,x_2z+y_2}`, pour un certain
        :math:`z` dans :math:`\left[0,p-1\right]`. Ils sont égaux si et
        seulement si :math:`x_1z+y_1=x_2z+y_2`, c'est-à-dire :

        .. math::
            \left(x_1-x_2\right)z &= y_2-y_1

        De deux choses l'une :

        * soit :math:`p` est un nombre premier, et alors il existe une unique
          solution :math:`z=\frac{y_2-y_1}{x_1-x_2}` (ces calculs se faisant
          toujours dans :math:`\mathbb{Z}/p\mathbb{Z}`, qui est alors un
          corps). Cela signifie que nos deux cartes ont un unique symbole en
          commun ;
        * soit :math:`p` n'est pas un nombre premier, et alors, pour l'un au
          moins des quadruplets :math:`x_1`, :math:`x_2`, :math:`y_1`,
          :math:`y_2`, l'équation :math:`\left(x_1-x_2\right)z=y_2-y_1` a
          plusieurs solutions (cela est du au fait que
          :math:`\mathbb{Z}/p\mathbb{Z}` n'est alors pas un corps). En
          conséquence, pour l'un au moins des couples de cartes, il y a
          plusieurs symboles en commun.

    * Couples de symboles

        Supposons qu'un couple de symboles apparaisse dans deux
        cartes différentes. Alors ces deux cartes ont plus d'un symbole en
        commun, et la configuration n'est pas valide, ce qui est contraire à ce
        qui a déjà été prouvé. Donc chaque couple apparait au plus une fois.

        Par construction, chaque symbole :math:`t_x`, et `d`, apparaissent une
        fois avec chacun des autres symboles. Soient deux symboles
        :math:`s_{z_1,i}` et :math:`s_{z_2,j}` (:math:`z_1\neq z_2`). On pose
        :math:`x=\frac{i-j}{z_1-z_2}` (ce nombre est bien défini si :math:`p`
        est un nombre premier, et :math:`z_1\neq z_2`), et :math:`y=i-xz_1`.
        Alors :math:`x\left(z_1-z_2\right)=i-j`, donc :math:`xz_1-xz_2=i-j`, et
        enfin :math:`j-xz_2=i-xz_1`. En notant que :math:`y=i-xz_1`, nous avons
        montré
        :math:`\left\{\begin{array}{c}y=i-xz_1\\y=j-xz_2\end{array}\right.`. En
        isolant :math:`i` et :math:`j` dans ce système, nous obtenons
        :math:`\left\{\begin{array}{c}i=xz_1+y\\j=xz_2+y\end{array}\right.`.
        Donc
        :math:`\left\{\begin{array}{c}s_{z_1,i}=s_{z_1,xz_1+y}=T_{x,y}[z_1]\\s_{z_2,j}=s_{z2,xz_2+y}=T_{x,y}[z_2]\end{array}\right.`.
        Et donc les deux symboles :math:`s_{z_1,i}` et :math:`s_{z_2,j}`
        apparaissent tous les deux sur la carte :math:`T_{x,y}`, aux rangs
        respectifs :math:`z_1` et :math:`z_2`.

    À ce stade, nous avons montré ici que l'algorithme produit une
    configuration valide si et seulement si :math:`p` est un nombre premier.


    * Nombre d'apparition de chaque symbole

        Par construction, chaque symbole apparait :math:`p+1` fois, donc chaque
        symbole apparait autant de fois.

    * Taille des cartes

        Par construction, chaque carte contient :math:`p+1` symboles, donc les
        cartes contiennent autant de symboles.

Mise en œuvre
-------------

.. literalinclude:: ../../jouets/dobble/__init__.py
    :linenos:
    :pyobject: genere_jeu

Conséquences
------------

Voici quelques conséquences de cet algorithme.

.. proof:property:: Création de configurations irrégulières

    Pour toute configuration régulière (contenant au moins deux cartes), il
    existe une configuration irrégulière valide (au moins) contenant une carte
    de moins.

.. proof:proof::

    Il suffit d'enlever une carte à une configuration régulière pour obtenir
    une configuration irrégulière valide.


.. proof:property:: Infinité du nombre de configurations

    Il existe un nombre infini de configurations valides, régulières et
    irrégulières.

.. proof:proof::

    Notre algorithme permet de créer une configuration régulière à
    :math:`p^2+p+1` cartes, quel que soit :math:`p` premier, et ces
    configurations sont toutes différentes. Il existe une infinité de nombres
    premiers (merci Euclide), donc il existe une infinité de configurations
    régulières.

    Les configurations régulières étant valides, il existe une infinité de
    configurations valides.

    Par la propriété précédente, pour chaque configuration régulière, on peut
    créer une configuration irrégulière ayant une carte de moins. Donc il
    existe une infinité de configurations irrégulières.

.. proof:property:: Configurations régulières de taille arbitrairement grande

    Il existe des configurations valides, régulières, et irrégulières ayant un
    nombre de cartes, de symboles différents, de symboles total, ou
    d'apparition de chaque symbole, arbitrairement grand.

.. proof:proof::

    Nous avons montré que pour chaque nombre premier :math:`p`, il existe une
    configuration régulière, pour laquelle le nombre de cartes, de symboles,
    etc. est une fonction croissante de :math:`p`. Donc il existe des
    configurations régulières de caractéristiques arbitrairement grande.

    Il est immédiat que le résultat est de même pour les configurations
    valides, et irrégulières.

.. _dobble_math_bilan:

Bilan
=====

Cette analyse (à la fois combinatoire et algorithmique) était interéssante, ou
au moins amusante, mais elle n'est pas complète, et plusieurs questions restent
en suspens.

* Toute configuration régulière est-elle générée par cet algorithme (à
  permutation des symboles près), ou existe-t-il des configurations qu'il ne
  capture pas ?

* Un cas particulier de cette question, posé par Bourrigan, est le suivant.
  Existe-t-il une configuration régulière à 157 cartes ?  C'est une question
  ouverte (c'est-à-dire que personne ne sait, dans le monde, si c'est
  possible). Notre algorithme ne permet pas de générer une telle configuration,
  mais cela ne veut pas dire pour autant qu'elle n'existe pas.

* En reprenant l'article de Bourrigan, on peut se demander si les
  configurations que je génère sont les même que celles qu'il étudie. Je pense
  que oui, mais je ne m'y connais pas assez en géométrie projective pour le
  prouver.

* J'ai l'intuition que pour un nombre de cartes donné, la configuration la plus
  intéressante à jouer (notion floue) est celle qui contient le plus de
  symboles par carte. Notre algorithme produit-il ce maximum ?

* Enfin, je me demande comment les concepteurs du jeu ont créés leur
  configuration. Ont-il fait une analyse similaire à la mienne ou à celle de
  Bourrigan ? Ont-ils tatonnés ? Ont-ils une autre méthode ?

