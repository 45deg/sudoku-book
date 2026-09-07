# 第5章 制約プログラミング サンプルプログラム

MiniZincで規則を宣言し、Gecodeで伝播と探索を行います。Pythonは入力の変換と盤面の検証を担当します。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

別途[MiniZinc](https://www.minizinc.org/software.html)のGecodeを含む配布版を導入し、`minizinc`をPATHから実行できるようにします。`minizinc --solvers`でGecodeが利用可能か確認できます。

## 実行例

```sh
uv run --frozen python examples/04-constraint-programming/solve.py fixtures/standard-9x9.sdk \
  --limit 2
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--limit {1,2}` | `1` | 取得する解の上限。ソルバーはGecodeに固定されており、CLIに`--solver`はありません。 |

## 入力を替えて試す

実行例の入力パスを次のいずれかに替えられます。問題の種類は入力について既知の性質であり、
この手法の出力だけでその性質を証明できるとは限りません。

| 問題 | 入力パス |
| --- | --- |
| 一意解 | `fixtures/standard-9x9.sdk` |
| 解なし | `fixtures/unsat-9x9.sdk` |
| 複数解 | `fixtures/multiple-9x9.sdk` |

掲載出力と実行条件の対応は、下記の生成スクリプトにも記録しています。

## 掲載結果の確認

保存済み出力との照合には、次を実行します。

```sh
uv run --frozen python examples/04-constraint-programming/generate_outputs.py --check
```
