============
数独を解こう
============

同じ数独を異なる計算手法へ翻訳し、モデルと解き方の違いを試す連載です。
各章では、その手法の考え方を数独へ当てはめ、実行できるサンプルを動かします。

最初から読む
============

.. toctree::
   :caption: はじめに
   :maxdepth: 1

   chapters/00-introduction

Part I 探索の仕組みを組み立てる
---------------------------------

.. toctree::
   :caption: Part I 探索の仕組みを組み立てる
   :maxdepth: 1

   chapters/01-backtracking
   chapters/02-exact-cover

Part II 規則を宣言して解く
---------------------------

.. toctree::
   :caption: Part II 規則を宣言して解く
   :maxdepth: 1

   chapters/03-prolog
   chapters/04-minikanren
   chapters/05-constraint-programming
   chapters/06-asp

Part III 論理式と状態を扱う
---------------------------

.. toctree::
   :caption: Part III 論理式と状態を扱う
   :maxdepth: 1

   chapters/07-sat
   chapters/08-smt
   chapters/09-bdd-model-counting
   chapters/10-model-checking

Part IV 数式と目的関数へ変換する
---------------------------------

.. toctree::
   :caption: Part IV 数式と目的関数へ変換する
   :maxdepth: 1

   chapters/11-integer-programming
   chapters/12-groebner-basis
   chapters/13-qubo

Part V 反復計算で候補を探す
----------------------------

.. toctree::
   :caption: Part V 反復計算で候補を探す
   :maxdepth: 1

   chapters/14-iterative-projection
   chapters/15-factor-graph

補遺
====

.. toctree::
   :caption: 補遺
   :maxdepth: 1

   appendices/01-further-methods
