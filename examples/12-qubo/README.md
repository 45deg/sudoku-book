# 第12章 QUBOと量子アニーリング (12-qubo) サンプルプログラム

QUBO (Quadratic Unconstrained Binary Optimization) 定式化による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: QUBO行列表現を作成しアニーリング/イジングソルバー等で解くプログラム
- `qubo.py`: QUBOハミルトニアン構築モジュール
- `penalty_example.py`: ペナルティ項の計算デモ
- `test_qubo.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`numpy`, `dwave-neal` / `pyqubo` 等)

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
# ペナルティ項デモの実行
python3 penalty_example.py

# 4x4数独盤面を解く
python3 solve.py examples/12-qubo/boards/standard-4x4.sdk --limit 2
```
