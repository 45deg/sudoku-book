# 第14章 反復射影 サンプルプログラム

局所制約への射影と複製を一致させる射影を組み合わせ、4×4数独を探します。数独ソルバーは本文のRRR更新を使い、小例だけが単純な交互射影です。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

## 実行例

```sh
uv run --frozen python examples/13-iterative-projection/small_projection.py
uv run --frozen python examples/13-iterative-projection/solve.py \
  examples/13-iterative-projection/boards/unique-4x4.sdk --seed 0 --max-iterations 2000 --beta 0.5 \
  --tolerance 1e-8
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--seed N` | `0` | 初期配列を作る乱数シード。 |
| `--max-iterations N` | `20000` | 反復上限（1以上）。掲載結果では2000を指定しています。 |
| `--beta X` | `0.5` | 更新量の係数（0より大きく1以下）。 |
| `--tolerance X` | `1e-8` | 残差の許容値（0以上）。 |

一回の実行で一盤面を探します。`--limit`はありません。解を得られない場合は`unknown`で、一意性や解なしは判定しません。

## 入力を替えて試す

実行例の入力パスを次のいずれかに替えられます。問題の種類は入力について既知の性質であり、
この手法の出力だけでその性質を証明できるとは限りません。

| 問題 | 入力パス |
| --- | --- |
| 一意解 | `examples/13-iterative-projection/boards/unique-4x4.sdk` |
| 解なし | `examples/13-iterative-projection/boards/unsat-4x4.sdk` |
| 複数解 | `fixtures/shidoku-4x4.sdk` |

複数解問題の掲載結果は`--seed 2 --max-iterations 2000`で得ています。ほかの二問は実行例と同じシード0です。

掲載出力と実行条件の対応は、下記の生成スクリプトにも記録しています。

## 掲載結果の確認

保存済み出力との照合には、次を実行します。

```sh
uv run --frozen python examples/13-iterative-projection/generate_outputs.py --check
```
