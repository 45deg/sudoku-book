# 第6章 SAT (06-sat) サンプルプログラム

SAT（命題論理適合性問題）ソルバーへのエンコーディングによる数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: 数独をCNFに変換しPySAT等で解くソルバー
- `proposition_demo.py`: 命題論理エンコーディングのデモ
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`python-sat` 等)

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
# 命題デモの実行
python3 proposition_demo.py

# 標準問題を解く（最大2解）
python3 solve.py fixtures/standard-9x9.sdk --limit 2
```
