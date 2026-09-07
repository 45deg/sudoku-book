# 第9章 BDDとモデル数え上げ サンプルプログラム

dd.autorefで4×4数独の二分決定図（BDD）を作り、全解数を数えます。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

## 実行例

```sh
uv run --frozen python examples/10-bdd-model-counting/small_bdd.py
uv run --frozen python examples/10-bdd-model-counting/solve.py \
  examples/10-bdd-model-counting/boards/unique-4x4.sdk --limit 2
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--limit N` | `2` | 表示する盤面数の上限（0以上）。0でも全解数は計算します。 |
| `--order {cell,digit}` | `cell` | 候補変数をマス優先または数字優先で並べます。BDDの大きさに影響します。 |

## 入力を替えて試す

実行例の入力パスを次のいずれかに替えられます。問題の種類は入力について既知の性質であり、
この手法の出力だけでその性質を証明できるとは限りません。

| 問題 | 入力パス |
| --- | --- |
| 一意解 | `examples/10-bdd-model-counting/boards/unique-4x4.sdk` |
| 解なし | `examples/10-bdd-model-counting/boards/unsat-4x4.sdk` |
| 複数解 | `fixtures/shidoku-4x4.sdk` |

掲載出力と実行条件の対応は、下記の生成スクリプトにも記録しています。

## 掲載結果の確認

保存済み出力との照合には、次を実行します。

```sh
uv run --frozen python examples/10-bdd-model-counting/generate_outputs.py --check
```
