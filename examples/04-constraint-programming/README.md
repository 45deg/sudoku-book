# 第4章 制約プログラミング (04-constraint-programming) サンプルプログラム

MiniZinc および CP ソルバーによる数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: MiniZincモデルを呼び出すPythonスクリプト
- `sudoku.mzn`: MiniZinc言語による数独の制約モデル定義
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上および MiniZinc CLI (`minizinc`)
- Gecode などの CP ソルバー（MiniZincに標準同梱）

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--solver SOLVER` (デフォルト: `gecode`)
  - 使用するCPソルバーの指定
- `--limit N` (デフォルト: `1`)
  - 探索する解の最大個数

### 実行例

```bash
# 標準問題を解く（最大2解）
python3 solve.py fixtures/standard-9x9.sdk --limit 2

# 解なし問題を判定する
python3 solve.py fixtures/unsat-9x9.sdk --limit 1

# 複数解問題を検証する
python3 solve.py fixtures/multiple-9x9.sdk --limit 2
```
