============================
第7章 SATで数独を解く
============================

左上のマスに1が入るか、2が入るか、という候補を真偽値で表します。「左上は1」を
表す変数が真なら、そのマスに1を置きます。同様に81個のマスと9個の数字を組み合わせると、
:math:`81\times9=729` 個の真偽変数ができます。

この729個へ、同じマスの候補を一つだけ真にする条件や、同じ行で同じ数字を重ねない条件を
加えます。すべての条件を満たす真偽値の組が、完成盤面に対応します。このように命題論理式を
満たす真偽値の割り当てを探す問題が
`SAT（充足可能性問題） <https://en.wikipedia.org/wiki/Boolean_satisfiability_problem>`_ です。

この章では、Pythonから `PySAT <https://pysathq.github.io/>`_ を使い、SAT専用ソルバーの
MiniSat 2.2へ論理式を渡します。Pythonは論理式への変換と盤面の復元を担当します。実際の探索は
MiniSatのCDCLアルゴリズムが行います :cite:labelpar:`een2003minisat` :cite:labelpar:`ignatiev2018pysat`。

二つの候補から一つを選ぶ
==========================

真か偽のどちらかを取る記号を **命題変数** と呼びます。変数 :math:`x_1` と :math:`x_2` の
ちょうど一方を真にする条件は、次の式で書けます。

:math:`\lor` はOR（少なくとも一方）、:math:`\land` はAND（両方）、:math:`\lnot` はNOT
（真偽の反転）を表します。

.. math::

   (x_1 \lor x_2) \land (\lnot x_1 \lor \lnot x_2)

前半は「少なくとも一つは真」、後半は「二つを同時に真にはしない」という条件です。
:math:`x_1` や :math:`\lnot x_1` を **リテラル**、リテラルをORでつないだ
:math:`(x_1\lor x_2)` を **節** と呼びます。節をANDでつないだ式は **連言標準形**、略して
CNFです。

.. list-table:: 二つの候補に対する式の真偽
   :header-rows: 1
   :widths: 15 15 25 25 20

   * - :math:`x_1`
     - :math:`x_2`
     - :math:`x_1\lor x_2`
     - :math:`\lnot x_1\lor\lnot x_2`
     - 式全体
   * - 偽
     - 偽
     - 偽
     - 真
     - 偽
   * - 偽
     - 真
     - 真
     - 真
     - 真
   * - 真
     - 偽
     - 真
     - 真
     - 真
   * - 真
     - 真
     - 真
     - 偽
     - 偽

PySATでは、変数を1以上の整数で表します。正の ``1`` は :math:`x_1`、負の ``-1`` は
:math:`\lnot x_1` です。一つの節は整数のリスト、CNF全体は節のリストになります。
式全体を真にする真偽値の割り当てを **モデル** と呼びます。

.. include:: ../examples/06-sat/proposition_demo.py
   :code: python
   :start-after: # BEGIN article-small-sat
   :end-before: # END article-small-sat

最初のモデルを得た後、その真偽値の組だけを禁止する節を追加します。この **ブロッキング節**
により、同じ論理式から次のモデルを探索します。結果は二通りです。

.. include:: ../outputs/06-sat-proposition.txt
   :literal:

たとえば最初のモデルが :math:`x_1=\mathrm{false}, x_2=\mathrm{true}` なら、追加する節は
:math:`x_1\lor\lnot x_2`、PySATのリストでは ``[1, -2]`` です。この節はその真偽値の組でだけ
偽になるため、同じモデルを除いてもう一方を残します。

数独でも、完成盤面に対応するモデルを禁止してもう一度解くことで、二つ目の解を調べます。

「ちょうど一つ」をCNFにする
============================

:math:`n` 個の変数 :math:`x_1,\ldots,x_n` のちょうど一つを真にするには、少なくとも一つを真にする
節を1個置きます。

.. math::

   x_1 \lor x_2 \lor \cdots \lor x_n

さらに、異なる二つの変数を同時に真にしない節を、すべての組に置きます。

.. math::

   \bigwedge_{1\le i<j\le n}(\lnot x_i \lor \lnot x_j)

後半には :math:`\binom{n}{2}` 個の節があります。数独では :math:`n=9` なので、9個の候補に対する
exactly-one制約は、長さ9の節1個と、長さ2の節36個です。

.. include:: ../examples/06-sat/solve.py
   :code: python
   :start-after: # BEGIN article-exactly-one
   :end-before: # END article-exactly-one

たとえば ``exactly_one([1, 2, 3])`` は、少なくとも一つを選ぶ ``[1, 2, 3]`` と、二つを同時に
選ばない ``[-1, -2]``、``[-1, -3]``、``[-2, -3]`` を返します。

この方式は、すべての組を直接並べるため **pairwise encoding** と呼ばれます。補助変数を使って
節数を減らす符号化もありますが、ここでは生成された節と数独の規則を対応させやすい方式を
選びました。PySAT自体も複数の基数制約符号化を提供しています
:cite:labelpar:`pysat197documentation`。

候補を729個の変数へ写す
=========================

行 :math:`r`、列 :math:`c` のマスに数字 :math:`d` が入ることを、命題変数
:math:`X_{r,c,d}` で表します。行と列は0から8、数字は1から9とします。Pythonのリストへ渡せる
整数IDは次の式で計算します。

.. math::

   v(r,c,d)=81r+9c+d

:math:`v(0,0,1)=1` で、最後の候補 :math:`v(8,8,9)=729` です。
たとえば :math:`v(0,0,5)=5` の ``5`` は数独へ入れる数値そのものではなく、「左上のマスが5」
という命題変数をMiniSatへ渡すための識別番号です。

.. include:: ../examples/06-sat/solve.py
   :code: python
   :start-after: # BEGIN article-variable
   :end-before: # END article-variable

数独のSAT符号化を研究したLynceとOuaknineも、この候補表現を使っています
:cite:labelpar:`lynce2006sudokuSat`。数字の大小や足し算は扱いません。729個は互いに独立した真偽変数であり、
整数IDは変数を区別する識別子として用います。この点で、第8章「SMT」で扱う整数や配列の理論とは
入力の意味が異なります。

四種類のexactly-one制約
========================

数独の規則を、次の四種類のグループへ分けます。

各マス
   :math:`X_{r,c,1},\ldots,X_{r,c,9}` のちょうど一つを真にします。グループは81個です。

行と数字
   行 :math:`r` のどの列に数字 :math:`d` を置くかを一つにします。行9本と数字9個で81個です。

列と数字
   列 :math:`c` のどの行に数字 :math:`d` を置くかを一つにします。これも81個です。

ブロックと数字
   各3×3ブロックで、数字 :math:`d` を置く場所を一つにします。9ブロックと9数字で81個です。

合計324個のグループがあり、一つにつき37節を生成します。初期配置を除くCNFは
:math:`324\times37=11{,}988` 節です。初期配置は、対応する :math:`X_{r,c,d}` を真にする長さ1の
節、つまり **単位節** として追加します。

.. include:: ../examples/06-sat/solve.py
   :code: python
   :start-after: # BEGIN article-encode
   :end-before: # END article-encode

四種類すべてへ「少なくとも一つ」と「高々一つ」を入れるため、同論文の分類では
拡張符号化（extended encoding）に当たります。数独の解を変えない重複した条件も含みますが、単位伝播で値が
決まりやすくなる利点があります :cite:labelpar:`lynce2006sudokuSat`。

``clauses`` は、そのまま
`DIMACS CNF <https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html>`_ に書き出せる形です。DIMACSでは
``p cnf 729 12013`` のようなヘッダーを書き、各節の末尾へ ``0`` を付けます。PySATのPython APIは
変数数を節から読み取るため、コード中ではヘッダーと末尾の ``0`` を省いています。

MiniSatはCNFをどう調べるか
==========================

.. list-table:: 人間とソルバーの役割分担
   :header-rows: 1
   :widths: 15 42 43

   * - 段階
     - 人間（Pythonコード）が行うこと
     - ソルバー（MiniSat）が行うこと
   * - 入力
     - 729個の命題変数を定義し、数独の規則をCNF（節のリスト）へ変換する
     - ―
   * - 探索
     - ―
     - CNFを受け取り、CDCL（単位伝播・決定・競合解析と節学習）で充足する割り当てを探す
   * - 出力
     - 正のリテラルを候補に戻し、盤面を復元・検証する
     - モデル（正負の整数のリスト）または ``UNSAT`` を返す

ここからは、ソルバー内部で行われる発展的な処理の概要です。MiniSat 2.2は **CDCL**
（Conflict-Driven Clause Learning）方式のSATソルバーです。探索中には、
おおむね次の処理が起こります。

単位伝播
   節のリテラルが一つだけ未確定で、ほかがすべて偽なら、残るリテラルを真にします。たとえば初期配置で
   :math:`X_{0,0,5}` が真になると、同じマスのpairwise節からほかの8候補が偽になります。

決定
   伝播だけで値が決まらなければ、未確定の変数を選んで真偽値を仮定します。どの変数を選ぶかは
   ソルバーのヒューリスティックが決めます。

競合解析と節学習
   ある節のリテラルがすべて偽になると競合です。CDCLは競合へ至った代入を解析し、同種の競合を
   避ける節を学習します。その節を使い、必要な位置まで代入を戻します。

MiniSatは、バックトラックへ単位伝播、節学習、非時系列の巻き戻しを組み合わせます。学習節は
元のCNFから論理的に導けるため、解を失わずに探索範囲を狭められます。CDCLの健全性と完全性は
SATの標準的な解説でも扱われています :cite:labelpar:`marquesSilva2009cdcl`。実装からは
`PySATのソルバーAPI <https://pysathq.github.io/docs/html/api/solvers.html>`_ を通して
MiniSatを呼び出します。

モデルを盤面へ戻す
==================

``Minisat22.get_model()`` は、正負の整数を並べたモデルを返します。正の整数に対応する候補だけを
集め、各マスで真になった数字を一つずつ取り出します。

.. include:: ../examples/06-sat/solve.py
   :code: python
   :start-after: # BEGIN article-decode
   :end-before: # END article-decode

各マスにexactly-one制約があるため、正しいモデルなら ``digits`` の長さは必ず1です。コードでも
この条件を確認し、CNF生成や復元処理の誤りを見逃さないようにしています。復元後の盤面は、さらに
共通検証器で行、列、ブロックと初期配置を検査します。

別解を探す
==========

一つのモデルを得た後、完成盤面で真だった81個の候補をすべて反転した節を追加します。たとえば
完成盤面の真の候補が :math:`p_1,\ldots,p_{81}` なら、ブロッキング節は次のとおりです。

.. math::

   \lnot p_1 \lor \lnot p_2 \lor \cdots \lor \lnot p_{81}

この節は、81個の候補がすべて再び真になる場合だけ偽です。ほかの完成盤面は残ります。

.. include:: ../examples/06-sat/solve.py
   :code: python
   :start-after: # BEGIN article-solve
   :end-before: # END article-solve

表示要求数より1個多くモデルの生成を試みます。後続の ``solve()`` が ``False`` を返す状態は、
追加されたブロッキング節によって解空間上の全解が走査され、解の列挙が完了したことを示します。

実行する
========

サンプルプログラムは :repo-dir:`examples/06-sat/` にあります。詳しい実行手順やオプションについては :repo-file:`examples/06-sat/README.md` を参照してください。

通常問題
--------

入力は ``fixtures/standard-9x9.sdk`` です。リポジトリ直下で次を実行します。

.. include:: ../fixtures/standard-9x9.sdk
   :literal:

.. code-block:: console

   $ uv run --frozen python examples/06-sat/solve.py fixtures/standard-9x9.sdk --limit 2

.. include:: ../outputs/06-sat-standard.txt
   :literal:

通常問題には25個の初期配置があるため、CNF全体で12,013節となります。最初に満たすモデルを得た後、その盤面を禁止するブロッキング節を追加して再度探索すると非充足となるため、一意解であることが判定できます。

解がない問題
------------

矛盾問題では、12,018節を同時に満たす割り当てが存在しません。初回の判定で非充足となるため、解なし（unsat）と確定します。

解が複数ある問題
----------------

複数解問題では、最初のモデルを禁止した後も2つ目のモデルが得られます。2つ目のモデルを禁止した段階で非充足となることから、解が全部で2つ存在することが判定されます。

この方法で分かること
====================

CNFの各モデルからは数独の完成盤面が一つ得られ、すべての完成盤面はCNFのモデルになります。
この対応があるため、MiniSatが ``SAT`` と返せば解が存在し、``UNSAT`` と返せば解は存在しません。
ブロッキング節を追加して二回目が ``UNSAT`` になれば一意解です。サンプルコードは乱数を
指定していません。モデルが見つかる順序はソルバーの版やヒューリスティックで変わる場合が
ありますが、SATかUNSATかという判定と解集合は変わりません。

pairwise encodingは、補助変数を使わずにexactly-one制約を読める点が長所です。その代わり、候補数
:math:`n` に対して節数が :math:`O(n^2)` になります。大きな数独や別の組合せ問題では、逐次カウンタ
など別の符号化が適する場合があります。どの符号化を選んでも、SATソルバーへ渡す前に問題を
真偽変数とCNFへ変換し、返されたモデルを元の問題へ戻す流れは共通です。

参考文献
========

.. include:: ../bibliography/generated/06-sat.rst
