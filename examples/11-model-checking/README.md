# 第11章 モデルチェッキング (11-model-checking) サンプルプログラム

モデルチェッキング (PyNuSMV / NuSMV 等) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: モデルチェッカを用いて数独の解を探すソルバー
- `small_example.py` / `small_example.smv`: SMV言語とモデル検証の動作デモ
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`pynusmv` 等)

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

# 4x4数独盤面を解く
python3 solve.py examples/11-model-checking/boards/standard-4x4.sdk --limit 2
```
