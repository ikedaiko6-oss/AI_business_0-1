"""Process a queue of YouTube URLs into note article drafts, one folder per video.

Queue file format: one YouTube URL per line. Blank lines and lines starting
with '#' are ignored, so you can use the file as an idea notebook. URLs that
were already processed are recorded in <out-dir>/processed.txt and skipped on
re-runs -- keep appending new URLs to the queue and re-run this script.

Run locally (Mac/Codex) where yt-dlp and whisper have real network access.

Usage:
    python batch.py queue.txt --out-dir ./output [--paid]
"""
import argparse
import hashlib
import re
from pathlib import Path

from transcribe import download_audio, transcribe_audio
from generate_article import generate_article
from make_eyecatch import make_eyecatch

VIDEO_ID_PATTERN = re.compile(r"(?:v=|/shorts/|youtu\.be/|/live/)([A-Za-z0-9_-]{11})")


def video_slug(url: str) -> str:
    match = VIDEO_ID_PATTERN.search(url)
    if match:
        return match.group(1)
    return hashlib.sha1(url.encode()).hexdigest()[:11]


def read_queue(queue_path: Path) -> list:
    urls = []
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("queue", help="Path to queue file (one YouTube URL per line)")
    parser.add_argument("--out-dir", default="./output")
    parser.add_argument("--whisper-model", default="small")
    parser.add_argument("--language", default="Japanese")
    parser.add_argument("--paid", action="store_true", help="Structure articles for paid sale (free preview + paid section)")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    processed_path = out_dir / "processed.txt"
    processed = set()
    if processed_path.exists():
        processed = {line.strip() for line in processed_path.read_text(encoding="utf-8").splitlines() if line.strip()}

    urls = read_queue(Path(args.queue))

    done, skipped, failed = 0, 0, []
    for url in urls:
        if url in processed:
            skipped += 1
            continue

        workdir = out_dir / video_slug(url)
        workdir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {url} -> {workdir} ===")
        try:
            audio_path = download_audio(url, workdir)
            txt_path = transcribe_audio(audio_path, workdir, args.whisper_model, args.language)
            transcript = txt_path.read_text(encoding="utf-8")
            article = generate_article(transcript, paid=args.paid)
            article_path = workdir / "article.md"
            article_path.write_text(article, encoding="utf-8")
            try:
                eyecatch_path = make_eyecatch(article_path, workdir / "eyecatch.png")
                print(f"Eyecatch: {eyecatch_path}")
            except Exception as exc:
                print(f"Eyecatch skipped ({exc}); article is still usable")
            with processed_path.open("a", encoding="utf-8") as f:
                f.write(url + "\n")
            done += 1
            print(f"OK: {article_path}")
        except Exception as exc:
            failed.append((url, str(exc)))
            print(f"FAILED: {exc}")

    print(f"\nDone: {done} generated, {skipped} skipped (already processed), {len(failed)} failed")
    for url, err in failed:
        print(f"  FAILED {url}: {err}")


if __name__ == "__main__":
    main()
