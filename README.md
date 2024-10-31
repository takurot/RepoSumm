# Repository Code Summarizer

このスクリプトは、リポジトリ内のコードおよび関連ファイル（`.py`, `.js`, `.ts`, `.c`, `.cpp`, `.md`, `.yaml`, `.json`）を解析し、OpenAI APIを利用して自動的に要約します。各ファイルの要約はMarkdownファイル `repo_summary.md` に書き出されます。

## 機能

- 指定されたディレクトリ以下のすべてのファイル（指定拡張子のみ）を再帰的に探索
- 各ファイルの内容をAIを用いて要約
- Markdown形式でファイルごとに要約を整理し、`repo_summary.md` に出力

## 必要な環境

- Python 3.x
- [OpenAI Pythonクライアントライブラリ](https://pypi.org/project/openai/)
  ```bash
  pip install openai argparse
  ```

## 設定

OpenAI APIキーが必要です。APIキーの設定は `OPENAI_API_KEY` の環境変数に設定してください。

## スクリプトの使い方

1. リポジトリのクローンまたはダウンロードを行います。
2. スクリプトの実行には、解析対象のリポジトリのルートディレクトリパスを指定する必要があります。
3. 以下のコマンドでスクリプトを実行し、Markdown形式の要約ファイルを生成します。

   ```bash
   python summarize_repo.py [repo_path]
   ```

   - `repo_path` で指定されたパスのディレクトリ以下のコードを要約します。
   - 生成された要約ファイル `repo_summary.md` は同じディレクトリに保存されます。

## 関数説明

- `summarize_code(code_snippet)`: OpenAI APIを使い、コードスニペットを要約。
- `process_file(file_path)`: 指定したファイルを読み込み、適切な長さに分割して各部分を要約。
- `process_directory(start_path)`: 指定されたディレクトリを再帰的に探索し、対応するファイルの要約を収集。
- `write_markdown(summaries, output_path="repo_summary.md")`: 要約をMarkdownファイルに書き出します。

## 注意

- OpenAI APIの利用には料金がかかるため、大量のファイルを要約する際にはコストが発生する可能性があります。
- AIによる要約のため、生成される内容は元のコードのニュアンスと若干異なる場合があります。内容の確認を推奨します。

## ライセンス

このスクリプトは自由に使用可能ですが、利用にあたってのライセンスについてはリポジトリ内の LICENSE ファイルをご確認ください。
