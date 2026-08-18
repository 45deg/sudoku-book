# 第9章 回答セットプログラミング (09-asp) サンプルプログラム

ASP (Answer Set Programming / Clingo) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: Pythonからclingo APIを呼び出して数独を解くソルバー
- `sudoku.lp`: 数独の規則を記述したASPプログラムファイル
- `choice.py` / `choice.lp`: 選択ルールのデモ用スクリプト
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照 (`clingo` 等)

```bash
pip install -r requirements.txt
```

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 探索する解（回答セット）の最大個数

### 実行例

```bash
# 選択ルールのデモを実行
python3 choice.py

# 標準問題を解く（最大2解）
python3 solve.py fixtures/standard-9x9.sdk --limit 2
```
