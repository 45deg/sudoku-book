# 第3章 miniKanren (03-minikanren) サンプルプログラム

miniKanren (kanren / logic) による数独ソルバーの実装例です。

## スクリプト構成

- `solve.py`: miniKanrenによる数独ソルバー
- `relation_demo.py`: 関係と言語機能のデモ用プログラム
- `test_solve.py`: ソルバーの自動テストスクリプト

## 依存環境

- Python 3.10 以上
- 依存ライブラリ: `requirements.txt` を参照（`kanren` 等）

```bash
pip install -r requirements.txt
```

## 実行方法と主な引数

```bash
python3 solve.py <入力盤面ファイル> [オプション]
```

### オプション一覧

- `--limit N` (デフォルト: `1`)
  - 探索する解の最大個数。`1` で最初の解で停止、`2` 以上で複数解の検証を行います。

### 実行例

```bash
# 関係デモの実行
python3 relation_demo.py

# 4x4数独を解く（一意性の確認）
python3 solve.py examples/03-minikanren/puzzles/unique-4x4.sdk --limit 2
```
