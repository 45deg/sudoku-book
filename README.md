# 数独を解こう

同じ数独を15通りの計算手法へ翻訳し、モデルと解き方の違いを、実行できるサンプルとともに紹介するオンラインブックです。

- [オンライン版](https://45deg.github.io/sudoku-book/)
- [GitHubリポジトリ](https://github.com/45deg/sudoku-book)

## ローカルでの確認

Python 3.11以降と[uv](https://docs.astral.sh/uv/)を使います。

```sh
uv sync --frozen
make render
```

生成物は `build/html/` に出力されます。ローカルサーバーで確認する場合は、次を実行して `http://localhost:8000/` を開きます。

```sh
make serve
```

原稿、サンプルコード、SVG、生成済み出力をまとめて検査するには `make check` を使います。一部の例では、SWI-Prolog、MiniZinc（Gecode）、nuXmvなどの外部処理系も必要です。各手法のREADMEに準備と実行の手順があります。詳しい執筆・検証方針は [AUTHORING.rst](AUTHORING.rst) を参照してください。

## デプロイ

`.github/workflows/deploy-pages.yml` は、`main` へのpushまたは手動実行時にSphinxでHTMLを生成し、GitHub Pagesへデプロイします。

初回のみ、GitHubリポジトリの **Settings → Pages → Build and deployment → Source** で **GitHub Actions** を選択してください。公開先は <https://45deg.github.io/sudoku-book/> です。
