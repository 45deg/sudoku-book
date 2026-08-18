# 第1章 バックトラック (01-backtracking) サンプルプログラム

バックトラック法による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: バックトラック法による数独ソルバー
- `test_solve.py`: ソルバーの自動テスト

## 依存環境

Python 3.10 以上（標準ライブラリのみで動作します）

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--method {naive,propagate}` (デフォルト: `propagate`)
  - `naive`: 候補の絞り込みを行わず、最初の空きマスから順に仮置きして探索する手法
  - `propagate`: 候補伝播（1行・1列・1ブロック内で確定した数字を除外）および MRV（残りの候補が最も少ないマスを優先）を組み合わせた手法
- `--limit N` (デフォルト: `1`)
  - 探索する解の最大個数。`1` を指定すると最初の解を見つけた時点で終了し、`2` 以上を指定すると複数解の有無を確認できます。

### 実行例

```bash
# Naive手法で解く（探索回数などの計測用）
python3 solve.py fixtures/standard-9x9.sdk --method naive --limit 1

# 候補伝播+MRV手法で解く
python3 solve.py fixtures/standard-9x9.sdk --method propagate --limit 1

# 解の一意性を確認する（最大2つまで解を探す）
python3 solve.py fixtures/standard-9x9.sdk --method propagate --limit 2
```
