# 第1章 バックトラック サンプルプログラム

盤面を直接操作するPython実装です。単純な探索と、候補伝播・MRVを組み合わせた探索を比較します。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

## 実行例

```sh
uv run --frozen python examples/01-backtracking/solve.py fixtures/standard-9x9.sdk --method \
  propagate --limit 2
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--method {naive,propagate}` | `propagate` | `naive` は最初の空きマスで規則に合う数字を試します。`propagate` は裸のシングル・隠れたシングルの伝播とMRVを使います。 |
| `--limit N` | `1` | 探索する解の上限（1以上）。一意性を調べるには2を指定し、探索完了も確認します。 |

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
uv run --frozen python tools/generate_outputs.py --check
```
