# note.com 記事自動生成パイプライン

YouTube動画 → 文字起こし → Claudeでnote記事生成 → note.comに下書き投稿、までを自動化するスクリプト群です。

## 前提

このパイプラインは **ローカル環境（Mac + Codex CLIなど、実インターネットにアクセスできる環境）で実行してください**。
Claude Codeのリモートサンドボックスはネットワークポリシーにより YouTube への接続がブロックされているため、
`transcribe.py` はそこでは動作しません。

## セットアップ

```bash
cd note_automation
pip install -r requirements.txt
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

whisper と yt-dlp が使えることを確認してください（既にMac上で動作確認済みのはず）。

## 使い方

### 1. 一括実行（推奨）

```bash
python main.py "https://youtube.com/shorts/xxxxx" --out-dir ./output
```

`output/article.md` にnote記事の下書きが生成されます。

note.comへの下書き投稿まで自動化する場合は `.env` に `NOTE_SESSION_COOKIE` を設定した上で:

```bash
python main.py "https://youtube.com/shorts/xxxxx" --publish
```

### 2. ステップごとに実行

```bash
# 文字起こしのみ
python transcribe.py "https://youtube.com/shorts/xxxxx" --out-dir ./output

# 記事生成のみ
python generate_article.py ./output/source.txt --out ./output/article.md

# note下書き投稿のみ
python post_note.py ./output/article.md
```

## note.com投稿について（重要）

note.comには記事投稿用の公式Public APIがありません。`post_note.py` はブラウザのログインセッション
Cookie（`note_gql_auth_token`）を使って内部APIを呼び出す非公式な方法です。

- 予告なく仕様が変わって動かなくなる可能性があります
- 自動投稿がnote.comの利用規約に抵触しないか、ご自身の判断で確認してください
- そのため本スクリプトは **下書き（draft）作成のみ** を行い、公開は手動で行う設計にしています

Cookie取得方法:
1. ブラウザでnote.comにログイン
2. devtools → Application → Cookies → note.com
3. `note_gql_auth_token` の値を `.env` の `NOTE_SESSION_COOKIE` にコピー

## 画像について

Canva / Freepikでの画像生成は現状手動です。記事の見出し構成 (`article.md`) を見ながら、
アイキャッチ・本文中の図解画像を作成し、note.comの下書き編集画面から手動でアップロードしてください。
