# CLAUDE.md — Guide for Creating New Tools

This file describes how to create new tools in this repository. All tools are single-file HTML single-page applications hosted via GitHub Pages.

Design ethos: [Useful patterns for building HTML tools](https://web.archive.org/web/20251210215112/https://simonwillison.net/2025/Dec/10/html-tools/) — Simon Willison, Dec 2025

---

## Core constraints

These are non-negotiable and apply to every tool:

1. **One file per tool.** Each tool is a single `.html` file. CSS and JavaScript are inlined inside it — no external stylesheets, no local JS files.
2. **No build step.** No npm, no webpack, no Vite, no TypeScript compilation. The file must run directly when opened in a browser.
3. **No React, no JSX, no frameworks with build requirements.** Use vanilla JavaScript only.
4. **Client-side only.** All logic runs in the browser. Do not call external APIs unless they are public, documented, and the user explicitly understands data is leaving their machine.
5. **CDN libraries only.** If a third-party library is needed, load it from a CDN (`jsDelivr`, `cdnjs`, `unpkg`). Do not vendor local copies.

---

## File naming

- Use lowercase, hyphen-separated names: `image-crop.html`, `json-formatter.html`
- Name the file after what the tool does, not what it uses
- Place all tools in the repo root

---

## HTML template

Start every new tool from this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Tool Name</title>
  <meta name="description" content="One sentence describing what this tool does.">
  <style>
    /* styles here */
    body {
      font-family: sans-serif;
      max-width: 800px;
      margin: 2rem auto;
      padding: 0 1rem;
    }
  </style>
</head>
<body>
  <h1>Tool Name</h1>
  <p>One sentence describing what this tool does.</p>

  <!-- tool UI here -->

  <footer>
    <p><a href="https://github.com/jschell/spa-tools/blob/main/tool-name.html">View source</a></p>
  </footer>

  <script>
    // all JavaScript here
  </script>
</body>
</html>
```

---

## Patterns to follow

### State management
Use plain JS variables and functions. No stores, no reactive frameworks. For simple state, update the DOM directly on events.

```js
let items = [];

function render() {
  document.getElementById('list').innerHTML = items
    .map(item => `<li>${escapeHtml(item)}</li>`)
    .join('');
}
```

### Escaping user input
Always escape untrusted content before inserting into the DOM. Never use `innerHTML` with raw user input.

```js
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
```

### Loading a CDN library
Prefer async loading. Check for availability before using.

```html
<script src="https://cdn.jsdelivr.net/npm/library@version/dist/library.min.js"></script>
```

Only add dependencies when the vanilla alternative would be significantly more complex. Note the library version explicitly in a comment.

### File/blob handling
Use the File API and `URL.createObjectURL` for download links.

```js
function download(filename, content, type = 'text/plain') {
  const blob = new Blob([content], { type });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}
```

### Drag and drop
Use standard `dragover` / `drop` events on a drop zone element.

```js
const zone = document.getElementById('drop-zone');
zone.addEventListener('dragover', e => e.preventDefault());
zone.addEventListener('drop', e => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  handleFile(file);
});
```

### Clipboard
```js
navigator.clipboard.writeText(text).then(() => {
  btn.textContent = 'Copied!';
  setTimeout(() => btn.textContent = 'Copy', 1500);
});
```

### URL state (shareable links)
Persist tool state in the URL hash or query string so users can share links to pre-filled tools.

```js
// Save
const params = new URLSearchParams({ input: inputEl.value });
history.replaceState(null, '', '?' + params.toString());

// Load on startup
const params = new URLSearchParams(location.search);
if (params.get('input')) inputEl.value = params.get('input');
```

---

## What makes a good tool

- **Does exactly one thing.** If you find yourself adding tabs or major sections, consider splitting into two tools.
- **Works offline.** After the initial page load (which fetches any CDN libraries), the tool should work without internet access.
- **No account required.** No login, no API keys baked in (if an API key is needed, the user pastes it in themselves and it stays in their browser).
- **Transparent.** Include a "View source" link in the footer pointing to the file on GitHub.
- **Short.** Most tools should be under 300 lines of HTML including styles and scripts.

---

## Companion docs file

Each tool has a companion `*.docs.md` file with the same base name as the HTML file:

- `epub-preparer.html` → `epub-preparer.docs.md`
- `json-formatter.html` → `json-formatter.docs.md`

The docs file contains a plain-prose description of what the tool does and how to use it — typically 1–3 short paragraphs. No headings, no code blocks. Write it as if describing the tool to someone who hasn't seen it.

```markdown
This tool does X. You can Y by doing Z. It also supports W.
```

---

## Registering a tool

After creating a new tool, run the update script to regenerate the tools table in `README.md` and the tools list in `index.html`:

```
python update-tools.py
```

The script reads the `<title>` and `<meta name="description">` from every `.html` file in the repo root (excluding `index.html`). Any file missing a `<title>` is silently ignored, so only intentional tools appear in the list.

Commit the `.html` file, the `.docs.md` file, and the updated `README.md` and `index.html` together.

---

## Testing

No test framework is used. Test by opening the `.html` file directly in a browser:

```
open tool-name.html          # macOS
xdg-open tool-name.html     # Linux
start tool-name.html         # Windows
```

Check that the tool:
- Loads without console errors
- Works with expected inputs
- Degrades gracefully on bad inputs (no crashes, useful error messages)
- Looks reasonable on a narrow viewport (mobile)

---

## Deploying

Commit the `.html` file to the `main` branch. GitHub Pages picks it up automatically within a minute or two.

```
https://jschell.github.io/spa-tools/tool-name.html
```

No CI, no build pipeline, no deployment commands needed.
