"""Download a YouTube video and transcribe it to text.

Run this on a machine with real internet access (your local Mac), not in a
sandboxed remote container that blocks YouTube traffic.

Usage:
    python transcribe.py <youtube_url> [--out-dir OUT_DIR] [--model small]
"""
import argparse
import subprocess
import sys
from pathlib import Path


def download_audio(url: str, out_dir: Path) -> Path:
    out_template = str(out_dir / "source.%(ext)s")
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android",
        "-f", "bestaudio/best",
        "-o", out_template,
        url,
    ]
    subprocess.run(cmd, check=True)
    downloaded = [p for p in out_dir.glob("source.*") if p.suffix not in {".txt", ".md"}]
    if not downloaded:
        raise RuntimeError("yt-dlp did not produce an output file")
    return downloaded[0]


def transcribe_audio(audio_path: Path, out_dir: Path, model: str, language: str) -> Path:
    cmd = [
        "whisper",
        str(audio_path),
        "--language", language,
        "--model", model,
        "--output_dir", str(out_dir),
        "--output_format", "txt",
    ]
    subprocess.run(cmd, check=True)
    txt_path = out_dir / f"{audio_path.stem}.txt"
    if not txt_path.exists():
        raise RuntimeError(f"Expected transcript at {txt_path} but it wasn't created")
    return txt_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--out-dir", default="./output", help="Directory for downloaded audio + transcript")
    parser.add_argument("--model", default="small", help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--language", default="Japanese", help="Spoken language for transcription")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading audio from {args.url} ...")
    audio_path = download_audio(args.url, out_dir)

    print(f"Transcribing {audio_path.name} with whisper ({args.model}) ...")
    txt_path = transcribe_audio(audio_path, out_dir, args.model, args.language)

    print(f"Transcript written to {txt_path}")


if __name__ == "__main__":
    main()
