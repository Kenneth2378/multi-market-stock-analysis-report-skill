#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader


PATTERNS = [r"file://", r"[A-Za-z]:/", r"[A-Za-z]:\\", r"/Users/", r"\\Users\\", r"api_key", r"token", r"cookie", r"secret", r"password"]


def extract_text(pdf: Path) -> str:
    return "\n".join((page.extract_text() or "") for page in PdfReader(str(pdf)).pages)


def scan(pdf: Path) -> dict:
    text = extract_text(pdf)
    hits = [pattern for pattern in PATTERNS if re.search(pattern, text, re.I)]
    return {"pdf": pdf.name, "extractor": "pypdf", "patterns": PATTERNS, "hits": hits, "status": "PASS" if not hits else "FAIL"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()
    result = scan(args.pdf)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
