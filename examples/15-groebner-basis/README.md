# 第12章 Boolean Gröbner基底 サンプルプログラム

初期配置のある4×4数独を、有理数係数の多項式と0-1条件で表します。SymPyでGröbner基底を計算し、全根から盤面を復元します。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

## 実行例

```sh
uv run --frozen python examples/15-groebner-basis/small_example.py
uv run --frozen python examples/15-groebner-basis/solve.py \
  examples/15-groebner-basis/boards/unique-4x4.sdk --basis-limit 4 --limit 2
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--limit N` | `2` | 表示する盤面数の上限（0以上）。内部では全解を復元します。 |
| `--basis-limit N` | `0` | 表示する基底の多項式数の上限（0以上）。0なら基底を表示しません。 |

## 入力を替えて試す

実行例の入力パスを次のいずれかに替えられます。問題の種類は入力について既知の性質であり、
この手法の出力だけでその性質を証明できるとは限りません。

| 問題 | 入力パス |
| --- | --- |
| 一意解 | `examples/15-groebner-basis/boards/unique-4x4.sdk` |
| 解なし | `examples/15-groebner-basis/boards/unsat-4x4.sdk` |
| 複数解 | `examples/15-groebner-basis/boards/multiple-4x4.sdk` |

掲載出力と実行条件の対応は、下記の生成スクリプトにも記録しています。

## 掲載結果の確認

保存済み出力との照合には、次を実行します。

```sh
uv run --frozen python examples/15-groebner-basis/generate_outputs.py --check
```
