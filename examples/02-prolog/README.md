# 第2章 Prolog (02-prolog) サンプルプログラム

Prolog（SWI-Prolog）による数独ソルバーの実装例です。

## スクリプト構成

- `solve.pl`: Prologによる数独ソルバー（CLIエントリーポイント）
- `facts_rules.pl`: 事実と規則のデモ用コード
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- SWI-Prolog (`swipl`) がインストールされている必要があります。

## 実行方法と主な引数

```bash
swipl -q -s solve.pl -- <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 探索する解の最大個数。`1` で最初の解で停止、`2` 以上で複数解の検証を行います。

### 実行例

```bash
# 標準問題を解く
swipl -q -s solve.pl -- fixtures/standard-9x9.sdk --limit 1

# 一意性を確認する（最大2つの解を探す）
swipl -q -s solve.pl -- fixtures/standard-9x9.sdk --limit 2
```
