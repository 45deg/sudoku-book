# 第13章 QUBO サンプルプログラム

dimodで数独のQUBOを作り、nealの古典的な焼きなまし法で4×4盤面を探します。CPU上で動作します。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

## 実行例

```sh
uv run --frozen python examples/12-qubo/penalty_example.py
uv run --frozen python examples/12-qubo/solve.py examples/12-qubo/boards/unique-4x4.sdk --seed \
  20260808 --reads 500 --sweeps 2000 --limit 2
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--seed N` | `20260808` | 乱数シード。 |
| `--reads N` | `500` | 焼きなましの実行回数（1以上）。 |
| `--sweeps N` | `2000` | 各実行で全変数を更新する巡回数（1以上）。 |
| `--limit N` | `2` | 表示する盤面数の上限（0以上）。サンプリング回数や発見数を制限する指定ではありません。 |

`distinct_valid_solutions_found`は標本中で得た異なる盤面数です。全解数ではありません。一盤面だけでは一意性を判定できず、解が見つからない場合は`unknown`を返します。

## 入力を替えて試す

実行例の入力パスを次のいずれかに替えられます。問題の種類は入力について既知の性質であり、
この手法の出力だけでその性質を証明できるとは限りません。

| 問題 | 入力パス |
| --- | --- |
| 一意解 | `examples/12-qubo/boards/unique-4x4.sdk` |
| 解なし | `examples/12-qubo/boards/unsat-4x4.sdk` |
| 複数解 | `examples/12-qubo/boards/multiple-4x4.sdk` |

掲載出力と実行条件の対応は、下記の生成スクリプトにも記録しています。

## 掲載結果の確認

保存済み出力との照合には、次を実行します。

```sh
uv run --frozen python examples/12-qubo/generate_outputs.py --check
```
