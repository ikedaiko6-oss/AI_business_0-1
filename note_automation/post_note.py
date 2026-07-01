"""Create a draft post on note.com from a generated article.

IMPORTANT: note.com has no official public API for creating posts. This
script uses note's internal browser API by replaying your logged-in
session cookie. It is unofficial, can break without notice, and may be
against note's Terms of Service for automated posting -- use at your own
risk and judgement. This script only creates a DRAFT; it does not
publish. Review and publish manually from your note.com dashboard.

Setup:
    1. Log in to note.com in your browser.
    2. Open devtools -> Application -> Cookies -> note.com
    3. Copy the value of the "note_gql_auth_token" cookie into
       NOTE_SESSION_COOKIE in your .env file.

Usage:
    python post_note.py article.md
"""
import argparse
import os
import re
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv()

NOTE_DRAFT_URL = "https://note.com/api/v1/text_notes"


def split_title_body(markdown_text: str):
    lines = markdown_text.strip().splitlines()
    title = "Untitled"
    body_lines = lines
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body_lines = lines[1:]
    body = "\n".join(body_lines).strip()
    return title, body


def create_draft(title: str, body: str, session_cookie: str) -> dict:
    headers = {
        "Cookie": f"note_gql_auth_token={session_cookie}",
        "Content-Type": "application/json",
    }
    payload = {"name": title, "body": body, "status": "draft"}
    response = requests.post(NOTE_DRAFT_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article", help="Path to article markdown file")
    args = parser.parse_args()

    session_cookie = os.environ.get("NOTE_SESSION_COOKIE")
    if not session_cookie:
        raise SystemExit("NOTE_SESSION_COOKIE is not set in your .env file")

    markdown_text = Path(args.article).read_text(encoding="utf-8")
    title, body = split_title_body(markdown_text)

    print(f"Creating draft: {title!r} ...")
    result = create_draft(title, body, session_cookie)
    print("Draft created. Review and publish manually at https://note.com/settings/drafts")
    print(result)


if __name__ == "__main__":
    main()
