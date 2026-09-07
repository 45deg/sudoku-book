# 第15章 因子グラフ サンプルプログラム

4×4数独の因子グラフでbelief propagationを反復し、各マスの重みから完成盤面を復元・検証します。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

## 実行例

```sh
uv run --frozen python examples/14-factor-graph/message_example.py
uv run --frozen python examples/14-factor-graph/solve.py \
  examples/14-factor-graph/boards/unique-4x4.sdk --method sum-product
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--method {sum-product,max-product}` | `sum-product` | 因子からのメッセージを、重みの和または最大値で求めます。 |
| `--max-iterations N` | `200` | 反復上限（1以上）。 |
| `--tolerance X` | `1e-10` | メッセージ変化の許容値（正の数）。 |
| `--damping X` | `0.5` | 更新時に前回のメッセージを残す割合（0以上1未満）。 |

一回の実行で一盤面を探します。`--limit`はありません。解を得られない場合は`unknown`で、一意性や解なしは判定しません。

## 入力を替えて試す

実行例の入力パスを次のいずれかに替えられます。問題の種類は入力について既知の性質であり、
この手法の出力だけでその性質を証明できるとは限りません。

| 問題 | 入力パス |
| --- | --- |
| 一意解 | `examples/14-factor-graph/boards/unique-4x4.sdk` |
| 解なし | `examples/14-factor-graph/boards/unsat-4x4.sdk` |
| 複数解 | `fixtures/shidoku-4x4.sdk` |

一意解問題では`--method max-product`も試します。ほかの二問の掲載結果は`sum-product`です。

掲載出力と実行条件の対応は、下記の生成スクリプトにも記録しています。

## 掲載結果の確認

保存済み出力との照合には、次を実行します。

```sh
uv run --frozen python examples/14-factor-graph/generate_outputs.py --check
```
