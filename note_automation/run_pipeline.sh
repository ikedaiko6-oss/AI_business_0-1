#!/usr/bin/env bash
# One-shot runner: clone/pull is assumed already done. This installs deps
# (if needed), asks for missing credentials interactively, then runs the
# full pipeline (download -> transcribe -> generate article -> note draft).
#
# Run this on a machine with real internet access (Mac/Codex), inside the
# note_automation/ directory:
#
#   ./run_pipeline.sh "https://youtube.com/shorts/xxxxx"
#
# Add --paid to generate a paid-article structure instead of a free one.
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <youtube_url> [--paid]"
  exit 1
fi

URL="$1"
shift
EXTRA_ARGS=("$@")

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

if [ -z "${NOTE_SESSION_COOKIE:-}" ] || [ "${NOTE_SESSION_COOKIE:-}" = "xxxxx" ]; then
  echo "note.comにログイン済みのブラウザで devtools > Application > Cookies > note.com"
  echo "の 'note_gql_auth_token' の値をコピーしてください。"
  read -rp "NOTE_SESSION_COOKIE を入力してください: " NOTE_SESSION_COOKIE
  sed -i.bak "s|^NOTE_SESSION_COOKIE=.*|NOTE_SESSION_COOKIE=${NOTE_SESSION_COOKIE}|" .env
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

python3 main.py "$URL" --out-dir ./output --publish "${EXTRA_ARGS[@]}"

echo ""
echo "完了しました。https://note.com/settings/drafts で下書きを確認し、内容をチェックしてから公開してください。"
