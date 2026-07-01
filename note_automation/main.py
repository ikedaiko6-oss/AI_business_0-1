"""End-to-end pipeline: YouTube video -> transcript -> note.com draft article.

Run this locally (Mac/Codex), where yt-dlp and whisper have real network
access. This orchestrates transcribe.py -> generate_article.py -> post_note.py.

Usage:
    python main.py <youtube_url> [--out-dir ./output] [--whisper-model small] [--publish]
"""
import argparse
from pathlib import Path

from transcribe import download_audio, transcribe_audio
from generate_article import generate_article
from make_eyecatch import make_eyecatch
from post_note import create_draft, split_title_body

import os
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--out-dir", default="./output")
    parser.add_argument("--whisper-model", default="small")
    parser.add_argument("--language", default="Japanese")
    parser.add_argument("--publish", action="store_true", help="Also create a note.com draft (requires NOTE_SESSION_COOKIE)")
    parser.add_argument("--paid", action="store_true", help="Structure the article for paid sale (free preview + paid section)")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Step 1/3: downloading + transcribing video ...")
    audio_path = download_audio(args.url, out_dir)
    txt_path = transcribe_audio(audio_path, out_dir, args.whisper_model, args.language)
    transcript = txt_path.read_text(encoding="utf-8")

    print("Step 2/3: generating note article with Claude ...")
    article = generate_article(transcript, paid=args.paid)
    article_path = out_dir / "article.md"
    article_path.write_text(article, encoding="utf-8")
    print(f"Article written to {article_path}")

    try:
        eyecatch_path = make_eyecatch(article_path, out_dir / "eyecatch.png")
        print(f"Eyecatch written to {eyecatch_path}")
    except Exception as exc:
        print(f"Eyecatch skipped ({exc}); article is still usable")

    if args.publish:
        print("Step 3/3: creating note.com draft ...")
        session_cookie = os.environ.get("NOTE_SESSION_COOKIE")
        if not session_cookie:
            raise SystemExit("NOTE_SESSION_COOKIE is not set in your .env file")
        title, body = split_title_body(article)
        result = create_draft(title, body, session_cookie)
        print("Draft created:", result)
    else:
        print("Step 3/3: skipped (pass --publish to also create a note.com draft)")


if __name__ == "__main__":
    main()
