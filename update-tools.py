#!/usr/bin/env python3
"""
update-tools.py

Scans .html files in the repo root for tool metadata and updates:
  - The tools table in README.md
  - The tools list in index.html

Run this after adding or updating a tool:
    python3 update-tools.py

Each tool's .html file must include:
    <title>Tool Name</title>
    <meta name="description" content="One sentence description.">

Files without a <title> tag are ignored (treated as non-tool HTML).
index.html is always excluded.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
EXCLUDE = {"index.html"}

README_START = "<!-- tools-start -->"
README_END = "<!-- tools-end -->"
INDEX_START = "<!-- tools-start -->"
INDEX_END = "<!-- tools-end -->"


def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_description(html: str) -> str:
    # Prefer <meta name="description" content="...">
    m = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    # Fallback: first <p> text content
    m = re.search(r"<p[^>]*>(.*?)</p>", html, re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return ""


def get_tools() -> list[dict]:
    tools = []
    for path in sorted(REPO_ROOT.glob("*.html")):
        if path.name in EXCLUDE:
            continue
        try:
            html = path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"  warning: could not read {path.name}: {e}", file=sys.stderr)
            continue
        title = extract_title(html)
        if not title:
            continue  # not a tool — skip silently
        tools.append(
            {
                "file": path.name,
                "title": title,
                "description": extract_description(html),
            }
        )
    return tools


def replace_section(text: str, start: str, end: str, new_content: str) -> str:
    """Replace content between start/end markers (inclusive of markers)."""
    pattern = rf"{re.escape(start)}.*?{re.escape(end)}"
    replacement = f"{start}\n{new_content}\n{end}"
    result, n = re.subn(pattern, replacement, text, flags=re.DOTALL)
    if n == 0:
        raise ValueError(f"Markers not found in file: {start!r} / {end!r}")
    return result


def update_readme(tools: list[dict]) -> None:
    path = REPO_ROOT / "README.md"
    text = path.read_text(encoding="utf-8")

    if tools:
        rows = "\n".join(
            f'| [{t["title"]}]({t["file"]}) | {t["description"]} |' for t in tools
        )
        table = f"| Tool | Description |\n|------|-------------|\n{rows}"
    else:
        table = "| Tool | Description |\n|------|-------------|\n| _(no tools yet)_ | |"

    path.write_text(replace_section(text, README_START, README_END, table), encoding="utf-8")
    print(f"  README.md updated ({len(tools)} tool(s))")


def update_index(tools: list[dict]) -> None:
    path = REPO_ROOT / "index.html"
    if not path.exists():
        print("  index.html not found — skipping")
        return

    text = path.read_text(encoding="utf-8")

    if tools:
        items = "\n".join(
            "      <li>"
            f'<a href="{t["file"]}">{t["title"]}</a>'
            + (f' &mdash; {t["description"]}' if t["description"] else "")
            + "</li>"
            for t in tools
        )
        content = f"<ul>\n{items}\n    </ul>"
    else:
        content = "<p>No tools yet. Check back soon.</p>"

    path.write_text(replace_section(text, INDEX_START, INDEX_END, content), encoding="utf-8")
    print(f"  index.html updated ({len(tools)} tool(s))")


def main() -> None:
    print("Scanning for tools...")
    tools = get_tools()
    if not tools:
        print("  No tools found (no .html files with <title> tags, excluding index.html)")
    else:
        print(f"  Found: {', '.join(t['file'] for t in tools)}")
    update_readme(tools)
    update_index(tools)
    print("Done.")


if __name__ == "__main__":
    main()
