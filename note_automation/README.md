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
```

whisper と yt-dlp が使えることを確認してください（既にMac上で動作確認済みのはず）。

## 使い方

### 0. 最速で1本通す（推奨）

初回のみ依存インストール後、これを実行すると対話式でAPIキー・note Cookieを聞かれ、
そのまま動画取得〜記事生成〜note下書き作成まで自動で完走します。

```bash
./run_pipeline.sh "https://youtube.com/shorts/xxxxx"
```

### 1. 手動で一括実行

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

### 3. 複数動画をまとめて処理（ネタ帳キュー）

`queue.example.txt` をコピーして `queue.txt` を作り、記事にしたい動画URLを1行ずつ追加:

```bash
python batch.py queue.txt --out-dir ./output
```

- `#`始まりの行と空行はメモとして無視されます
- 処理済みURLは `output/processed.txt` に記録され、再実行時は自動でスキップ。ネタ帳に追記して再実行するだけで新規分だけ処理されます
- 動画ごとに `output/<動画ID>/article.md` が生成されます

### 4. 有料記事モード（収益化）

`main.py` / `batch.py` / `generate_article.py` に `--paid` を付けると、
**無料部分（共感導入＋得られる結果の提示）→「====== ここから有料 ======」→ 有料部分（具体的ノウハウ全て）**
という販売用の構成で生成されます。noteのエディタで、この境界行の位置に有料ラインを設定してください。
記事末尾に推奨販売価格もコメントで提案されます。

また、通常モード・有料モードとも記事末尾に**推奨ハッシュタグ**（5〜8個）が自動提案されるようになりました。
noteの発見性はハッシュタグの影響が大きいので、公開時に設定してください。

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

アイキャッチ画像（1280x670）は自動生成されます。`main.py` / `batch.py` の実行時に、
記事タイトルからグラデーション背景のアイキャッチ（`eyecatch.png`）がPillowでローカル生成されます。
API不要・無料・オフラインで動くので、Codex環境でそのまま動きます。単体実行も可能:

```bash
python make_eyecatch.py ./output/article.md --out ./output/eyecatch.png
```

- デザインを変えたい場合は `make_eyecatch.py` 冒頭の色定数（`TOP_COLOR` 等）を編集
- よりリッチなイラスト系画像が欲しい場合は、OpenAIの画像API（gpt-image-1）を呼ぶ形に差し替え可能（Codexから実行できる）
- 本文中の図解やこだわりのアイキャッチはCanva / Freepikで手動作成し、下書き編集画面でアップロード

## 運用のコツ（月7桁を目指すフェーズ設計）

1. **フェーズ1: 無料記事でフォロワー獲得**（今ここ）
   `queue.txt` にネタをためて `batch.py` で量産 → 毎日1本公開。スキ・フォローの反応をメモする
2. **フェーズ2: 伸びたテーマを深掘り**
   反応が良かった記事のテーマで、より具体的・実践的な記事を作る
3. **フェーズ3: 有料化**
   `--paid` で有料記事構成を生成し、フォロワーが十分ついたテーマから数百円で販売開始
4. **フェーズ4: マガジン化・単価アップ**
   有料記事が売れ始めたら、シリーズをまとめた有料マガジンや高単価記事へ展開
