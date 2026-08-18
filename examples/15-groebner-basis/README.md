# 第15章 グレブナー基底 (15-groebner-basis) サンプルプログラム

代数幾何・多項式イデアルのグレブナー基底 (Gröbner Basis / SymPy) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: 多項式系を構成しグレブナー基底を計算して数独を解くソルバー
- `small_example.py`: 小規模多項式環とグレブナー基底の計算デモ
- `test_groebner_basis.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`sympy` 等)

```bash
pip install -r requirements.txt
```

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 探す解の最大個数

### 実行例

```bash
# 小規模デモの実行
python3 small_example.py

# 4x4数独盤面を解く
python3 solve.py examples/15-groebner-basis/boards/standard-4x4.sdk --limit 2
```
