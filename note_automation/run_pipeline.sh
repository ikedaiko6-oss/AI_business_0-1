#!/usr/bin/env bash
# One-shot runner: clone/pull is assumed already done. This installs deps
# (if needed), asks for missing credentials interactively, then runs the
# pipeline (download -> transcribe -> generate article -> eyecatch).
#
# By default this STOPS before posting to note.com -- it only needs your
# ANTHROPIC_API_KEY, not a note.com login. You review output/article.md and
# output/eyecatch.png yourself, then copy/paste + upload them into note's
# editor after logging in manually.
#
# Run this on a machine with real internet access (Mac/Codex), inside the
# note_automation/ directory:
#
#   ./run_pipeline.sh "https://youtube.com/shorts/xxxxx"
#
# Add --paid to generate a paid-article structure instead of a free one.
# Add --publish to also auto-create a note.com draft via NOTE_SESSION_COOKIE
# (you'll be prompted for the cookie only in that case).
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <youtube_url> [--paid] [--publish]"
  exit 1
fi

URL="$1"
shift
EXTRA_ARGS=("$@")

PUBLISH=0
for arg in "${EXTRA_ARGS[@]}"; do
  if [ "$arg" = "--publish" ]; then
    PUBLISH=1
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
fi

# shellcheck disable=SC1091
source .env 2>/dev/null || true

if [ -z "${ANTHROPIC_API_KEY:-}" ] || [ "${ANTHROPIC_API_KEY:-}" = "sk-ant-xxxxx" ]; then
  read -rp "ANTHROPIC_API_KEY を入力してください: " ANTHROPIC_API_KEY
  sed -i.bak "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}|" .env
fi

if [ "$PUBLISH" -eq 1 ]; then
  if [ -z "${NOTE_SESSION_COOKIE:-}" ] || [ "${NOTE_SESSION_COOKIE:-}" = "xxxxx" ]; then
    echo "note.comにログイン済みのブラウザで devtools > Application > Cookies > note.com"
    echo "の 'note_gql_auth_token' の値をコピーしてください。"
    read -rp "NOTE_SESSION_COOKIE を入力してください: " NOTE_SESSION_COOKIE
    sed -i.bak "s|^NOTE_SESSION_COOKIE=.*|NOTE_SESSION_COOKIE=${NOTE_SESSION_COOKIE}|" .env
  fi
fi
rm -f .env.bak

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "yt-dlp が見つかりません。'pip install -r requirements.txt' を先に実行してください。"
  exit 1
fi
if ! command -v whisper >/dev/null 2>&1; then
  echo "whisper が見つかりません。'pip install -r requirements.txt' を先に実行してください。"
  exit 1
fi

python3 main.py "$URL" --out-dir ./output "${EXTRA_ARGS[@]}"

echo ""
if [ "$PUBLISH" -eq 1 ]; then
  echo "完了しました。https://note.com/settings/drafts で下書きを確認し、内容をチェックしてから公開してください。"
else
  echo "完了しました。note.comにログインし、下記を手動でコピー&アップロードしてください:"
  echo "  記事本文: $SCRIPT_DIR/output/article.md"
  echo "  アイキャッチ画像: $SCRIPT_DIR/output/eyecatch.png"
fi
