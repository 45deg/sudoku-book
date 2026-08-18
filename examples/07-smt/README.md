# 第7章 SMT (07-smt) サンプルプログラム

SMT（満足度モジュロ理論）ソルバー (Z3) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: SMT理論（整数理論など）を用いた数独ソルバー
- `small_example.py`: SMT制約記述の小規模デモ
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`z3-solver` 等)

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
