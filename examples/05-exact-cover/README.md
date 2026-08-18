# 第5章 Exact Cover と Algorithm X (05-exact-cover) サンプルプログラム

Algorithm X (DLX / Exact Cover) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: Exact Cover行列への定式化とAlgorithm Xによる数独ソルバー
- `exact_cover.py`: DLX（Dancing Links）またはExact Cover探索のコアロジック
- `toy.py`: 小規模トイモデルでの動作確認用スクリプト
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上（標準ライブラリのみで動作します）

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 探索する解の最大個数

### 実行例

```bash
# トイモデルの実行
python3 toy.py

# 標準問題を解く（最大2解）
python3 solve.py fixtures/standard-9x9.sdk --limit 2
```
