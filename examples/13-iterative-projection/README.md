# 第13章 交互投影法 (13-iterative-projection) サンプルプログラム

交互投影法（Iterative Projection / ADMM 等）による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: 交互投影アルゴリズムによる連続緩和と投影処理ソルバー
- `small_projection.py`: 2次元/低次元における投影処理のデモ
- `test_iterative_projection.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`numpy`, `scipy` 等)

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
# 投影処理デモの実行
python3 small_projection.py

# 4x4数独盤面を解く
python3 solve.py examples/13-iterative-projection/boards/standard-4x4.sdk --limit 2
```
