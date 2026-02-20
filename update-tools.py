#!/usr/bin/env python3
"""
update-tools.py

Scans .html files in the repo root for tool metadata and updates:
  - The tools table in README.md
  - The tools list in index.html
  - A "Last updated" timestamp in each tool's HTML (before </body>)

Run this after adding or updating a tool:
    python3 update-tools.py

Each tool's .html file must include:
    <title>Tool Name</title>
    <meta name="description" content="One sentence description.">

Files without a <title> tag are ignored (treated as non-tool HTML).
index.html is always excluded.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent
EXCLUDE = {"index.html"}

README_START = "<!-- tools-start -->"
README_END = "<!-- tools-end -->"
INDEX_START = "<!-- tools-start -->"
INDEX_END = "<!-- tools-end -->"
MODIFIED_START = "<!-- last-modified-start -->"
MODIFIED_END = "<!-- last-modified-end -->"


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


def get_git_date(path: Path) -> str:
    """Return the date of the last git commit touching this file (YYYY-MM-DD), or ''."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ad", "--date=format:%Y-%m-%d", "-1", "--", str(path)],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return result.stdout.strip()
    except Exception:
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
                "path": path,
                "title": title,
                "description": extract_description(html),
                "last_modified": get_git_date(path),
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
            f'| [{t["title"]}]({t["file"]}) | {t["description"]} | {t["last_modified"] or "—"} |'
            for t in tools
        )
        table = f"| Tool | Description | Updated |\n|------|-------------|--------|\n{rows}"
    else:
        table = "| Tool | Description | Updated |\n|------|-------------|--------|\n| _(no tools yet)_ | | |"

    path.write_text(replace_section(text, README_START, README_END, table), encoding="utf-8")
    print(f"  README.md updated ({len(tools)} tool(s))")


def update_index(tools: list[dict]) -> None:
    path = REPO_ROOT / "index.html"
    if not path.exists():
        print("  index.html not found — skipping")
        return

    text = path.read_text(encoding="utf-8")

    if tools:
        items = []
        for t in tools:
            date_badge = (
                f' <span style="color:#888;font-size:0.8em">({t["last_modified"]})</span>'
                if t["last_modified"]
                else ""
            )
            items.append(
                "      <li>"
                f'<a href="{t["file"]}">{t["title"]}</a>'
                + (f' &mdash; {t["description"]}' if t["description"] else "")
                + date_badge
                + "</li>"
            )
        content = "<ul>\n" + "\n".join(items) + "\n    </ul>"
    else:
        content = "<p>No tools yet. Check back soon.</p>"

    path.write_text(replace_section(text, INDEX_START, INDEX_END, content), encoding="utf-8")
    print(f"  index.html updated ({len(tools)} tool(s))")


def inject_last_modified(path: Path, date: str) -> None:
    """Insert or update the last-modified timestamp in a tool's HTML file."""
    html = path.read_text(encoding="utf-8")
    block = (
        f"{MODIFIED_START}"
        f'<p style="text-align:center;font-size:0.75rem;opacity:0.5;margin:0.5rem 0 0">'
        f"Last updated: {date}"
        f"</p>"
        f"{MODIFIED_END}"
    )
    if MODIFIED_START in html:
        pattern = rf"{re.escape(MODIFIED_START)}.*?{re.escape(MODIFIED_END)}"
        html = re.sub(pattern, block, html, flags=re.DOTALL)
    else:
        html = html.replace("</body>", f"{block}\n</body>", 1)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    print("Scanning for tools...")
    tools = get_tools()
    if not tools:
        print("  No tools found (no .html files with <title> tags, excluding index.html)")
    else:
        print(f"  Found: {', '.join(t['file'] for t in tools)}")
    update_readme(tools)
    update_index(tools)
    for t in tools:
        if t["last_modified"]:
            inject_last_modified(t["path"], t["last_modified"])
            print(f"  {t['file']}: injected last-modified {t['last_modified']}")
        else:
            print(f"  {t['file']}: no git date found — skipping last-modified injection")
    print("Done.")


if __name__ == "__main__":
    main()
