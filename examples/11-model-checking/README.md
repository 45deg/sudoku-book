# 第10章 モデル検査 サンプルプログラム

盤面を状態遷移系へ変換し、nuXmv 2.2.0の限定モデル検査（BMC）で完成盤面へ至る反例経路を求めます。

## 実行環境

以下のコマンドは、`pyproject.toml` と `fixtures/` があるリポジトリ直下で実行します。
Python 3.11以降とuvを使い、ロックファイルに記録した依存関係を準備します。

```sh
uv sync --frozen
```

別途[公式配布ページ](https://nuxmv.fbk.eu/download.html)からOSに合うnuXmv 2.2.0を取得し、展開します。Pythonの外部パッケージは使いません。
配布物の実行ファイルまたは起動スクリプトをPATHに追加するか、その絶対パスを環境変数`NUXMV`に設定してから以下を実行してください。単発の実行では`--nuxmv PATH`でも指定できます。
macOS版では、展開先の`usr/local/bin/nuXmv.sh`を指定します。このスクリプトが同梱ライブラリの場所を設定して起動するため、配布物のディレクトリ構成を保ってください。
利用条件は[公式ライセンス](https://nuxmv.fbk.eu/license.html)を参照してください。

## 実行例

```sh
uv run --frozen python examples/11-model-checking/small_example.py
uv run --frozen python examples/11-model-checking/solve.py fixtures/standard-9x9.sdk --limit 2
```

## オプション

| 指定 | 既定値 | 意味 |
| --- | --- | --- |
| `--limit {1,2}` | `1` | 取得する盤面の上限。2なら最初の完成盤面を目標から除外して再検査します。 |
| `--nuxmv PATH` | 自動検出 | nuXmvの実行ファイルまたは起動スクリプトへのパス。省略時は環境変数`NUXMV`、PATH上の`nuXmv.sh`、`nuXmv`の順で探します。 |

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
uv run --frozen python examples/11-model-checking/generate_outputs.py --check
```
