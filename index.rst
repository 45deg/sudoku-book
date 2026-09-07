============
数独を解こう
============

.. raw:: html

   <div class="book-home">
     <section class="home-hero" aria-labelledby="home-title">
       <p class="home-kicker">A computational tour of Sudoku</p>
       <h1 id="home-title">ひとつの数独、<br>15通りの考え方。</h1>
       <p class="home-lead">同じ盤面を、探索・論理・数式・反復計算へ翻訳する。<br>解を探すだけでなく、問題をどう表現するかをたどるオンラインブックです。</p>
       <div class="home-actions"><a class="home-button home-button-primary" href="chapters/00-introduction.html">最初から読む <span aria-hidden="true">→</span></a><a class="home-button home-button-secondary" href="https://github.com/45deg/sudoku-book">GitHubでソースを見る <span aria-hidden="true">↗</span></a></div>
       <div class="sudoku-mark" aria-hidden="true">
         <span>5</span><span></span><span></span><span></span><span>7</span><span></span><span></span><span></span><span></span><span>6</span><span></span><span></span><span>1</span><span>9</span><span>5</span><span></span><span></span><span></span><span></span><span>9</span><span>8</span><span></span><span></span><span></span><span></span><span>6</span><span></span><span>8</span><span></span><span></span><span></span><span>6</span><span></span><span></span><span></span><span>3</span><span>4</span><span></span><span></span><span>8</span><span></span><span>3</span><span></span><span></span><span>1</span><span>7</span><span></span><span></span><span></span><span>2</span><span></span><span></span><span></span><span>6</span><span></span><span>6</span><span></span><span></span><span></span><span></span><span>2</span><span>8</span><span></span><span></span><span></span><span></span><span>4</span><span>1</span><span>9</span><span></span><span></span><span>5</span><span></span><span></span><span></span><span></span><span>8</span><span></span><span></span><span>7</span><span>9</span>
       </div>
     </section>
     <section class="home-intro" aria-labelledby="what-is-this"><div><p class="section-label">この本でやること</p><h2 id="what-is-this">数独は、小さくて<br>奥行きのある実験場。</h2></div><p>数独の規則はシンプルです。それでも、手続きを書くことも、論理式を満たすことも、最適化問題を解くこともできます。各章ではひとつの手法を選び、モデル、コード、実行結果を並べて見ていきます。</p></section>
     <section class="home-journey" aria-labelledby="journey-title"><div class="section-heading"><div><p class="section-label">15 chapters · 5 perspectives</p><h2 id="journey-title">解法の地図</h2></div><a href="chapters/00-introduction.html">序章からはじめる →</a></div><div class="method-grid"><a class="method-card" href="chapters/01-backtracking.html"><span class="method-number">I</span><strong>探索を組み立てる</strong><span>バックトラック / Exact Cover</span></a><a class="method-card" href="chapters/03-prolog.html"><span class="method-number">II</span><strong>規則を宣言する</strong><span>Prolog / miniKanren / CP / ASP</span></a><a class="method-card" href="chapters/07-sat.html"><span class="method-number">III</span><strong>論理式と状態を扱う</strong><span>SAT / SMT / BDD / モデル検査</span></a><a class="method-card" href="chapters/11-integer-programming.html"><span class="method-number">IV</span><strong>数式へ変換する</strong><span>整数計画法 / Gröbner基底 / QUBO</span></a><a class="method-card" href="chapters/14-iterative-projection.html"><span class="method-number">V</span><strong>候補を反復する</strong><span>反復射影 / 因子グラフ</span></a></div></section>
     <section class="home-notes" aria-label="本の特徴"><div><span>01</span><h2>動かせる</h2><p>各手法に実行できるサンプルコードと、生成済みの出力を添えています。</p></div><div><span>02</span><h2>比べられる</h2><p>同じ問題を使うから、表現と解法の差に集中できます。</p></div><div><span>03</span><h2>たどり着ける</h2><p>前提知識を積み上げながら、異なる計算モデルへ進みます。</p></div></section>
   </div>

.. toctree::
   :hidden:
   :maxdepth: 1

   chapters/00-introduction
   chapters/01-backtracking
   chapters/02-exact-cover
   chapters/03-prolog
   chapters/04-minikanren
   chapters/05-constraint-programming
   chapters/06-asp
   chapters/07-sat
   chapters/08-smt
   chapters/09-bdd-model-counting
   chapters/10-model-checking
   chapters/11-integer-programming
   chapters/12-groebner-basis
   chapters/13-qubo
   chapters/14-iterative-projection
   chapters/15-factor-graph
   chapters/16-summary
   appendices/01-further-methods
