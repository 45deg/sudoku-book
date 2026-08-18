# 第14章 ファクターグラフと確率的伝播 (14-factor-graph) サンプルプログラム

ファクターグラフ (Factor Graph) および Belief Propagation (確率的伝播法) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: 確率的伝播法 (Belief Propagation) を用いた数独ソルバー
- `message_example.py`: ノード間メッセージ伝播の動作デモ
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`numpy` 等)

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
# メッセージ伝播デモの実行
python3 message_example.py

# 4x4数独盤面を解く
python3 solve.py examples/14-factor-graph/boards/standard-4x4.sdk --limit 2
```
