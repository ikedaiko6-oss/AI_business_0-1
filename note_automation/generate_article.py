"""Turn a video transcript into a note.com article draft using Claude.

Usage:
    python generate_article.py transcript.txt --out article.md
"""
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
import anthropic

load_dotenv()

SYSTEM_PROMPT = """あなたはnote.com向けの記事編集者です。
与えられた動画の文字起こしを元に、読みやすいnote記事を作成してください。

構成:
1. 目を引くタイトル（1行目に「# 」で記載）
2. 導入（読者の課題に共感する2-3文）
3. 本文（見出しを使い、具体的な手順やポイントを整理。文字起こしにある冗長な話し言葉は整理し、簡潔な文章にする）
4. まとめ（次のアクションを促す1段落）

文字起こしに無い情報を捏造しないこと。話し言葉のフィラー（「えー」「あの」等）は削除すること。
Markdown形式で出力してください。
"""


def generate_article(transcript: str, model: str = "claude-opus-4-8") -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    with client.messages.stream(
        model=model,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"以下は動画の文字起こしです。これを元にnote記事を作成してください。\n\n{transcript}"}
        ],
    ) as stream:
        final_message = stream.get_final_message()

    text_blocks = [block.text for block in final_message.content if block.type == "text"]
    return "\n".join(text_blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", help="Path to transcript .txt file")
    parser.add_argument("--out", default="article.md", help="Path to write generated article")
    parser.add_argument("--model", default="claude-opus-4-8")
    args = parser.parse_args()

    transcript = Path(args.transcript).read_text(encoding="utf-8")
    article = generate_article(transcript, model=args.model)

    Path(args.out).write_text(article, encoding="utf-8")
    print(f"Article written to {args.out}")


if __name__ == "__main__":
    main()
