# 第8章 整数計画法 (08-integer-programming) サンプルプログラム

整数計画法 (ILP/MIP) ソルバー (HiGHS / SciPy 等) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: 0-1整数計画問題として定式化し解くソルバー
- `small_example.py`: 整数計画定式化の小規模デモ
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`scipy` / `highs` 等)

```bash
pip install -r requirements.txt
```

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 探索する解の最大個数

### 実行例

```bash
# 小規模デモの実行
python3 small_example.py

# 標準問題を解く（最大2解）
python3 solve.py fixtures/standard-9x9.sdk --limit 2
```
