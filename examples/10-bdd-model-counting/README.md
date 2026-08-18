# 第10章 BDDとモデルカウンティング (10-bdd-model-counting) サンプルプログラム

BDD（二分決定グラフ）およびモデルカウンティングによる数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: BDDを用いた数独解法および解のカウントを行うソルバー
- `small_bdd.py`: 小規模BDD構築のデモ
- `bdd_utils.py`: BDD構築のユーティリティ関数
- `test_bdd_model_counting.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`dd` 等)

```bash
pip install -r requirements.txt
```

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 抽出・確認する解の最大個数

### 実行例

```bash
# 小規模BDDデモの実行
python3 small_bdd.py

# 4x4数独盤面を解く
python3 solve.py examples/10-bdd-model-counting/boards/standard-4x4.sdk --limit 2
```
