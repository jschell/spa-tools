# spa-tools

A collection of single-file HTML tools hosted via GitHub Pages.

Live site: https://jschell.github.io/spa-tools/

## Philosophy

These tools follow the design ethos described by [Simon Willison](https://web.archive.org/web/20251210215112/https://simonwillison.net/2025/Dec/10/html-tools/):

- **Single file.** Each tool is a self-contained `.html` file with all CSS and JavaScript inlined. No build step, no bundler, no framework. A tool can be shared as a single file or copy-pasted out of an LLM response.
- **No React.** Vanilla JavaScript only. JSX requires a build step, which adds friction. These tools stay simple.
- **CDN dependencies only.** If a library genuinely helps, load it from a CDN (jsDelivr, cdnjs, unpkg). Fewer dependencies are better.
- **Small and focused.** Each tool does one thing well. Keep it short, keep it readable.
- **Client-side only.** All processing happens in the browser. No servers, no accounts, no data sent anywhere.

## Tools

<!-- tools-start -->
| Tool | Description |
|------|-------------|
| [EPUB Preparer](epub-preparer.html) | Edit EPUB metadata, strip Project Gutenberg boilerplate, and download the corrected file. |
<!-- tools-end -->

## Development

See [CLAUDE.md](CLAUDE.md) for detailed instructions on creating new tools.

### Quick start

1. Copy an existing `.html` tool as a starting point
2. Edit it directly — no `npm install`, no build commands
3. Open the file in a browser to test
4. Commit and push — GitHub Pages serves it automatically

## Hosting

Tools are served as static files via [GitHub Pages](https://pages.github.com/).

**Setup (one-time):** Repository Settings → Pages → Source → Deploy from a branch → `main` / `root`.

Each `.html` file in the repo root is immediately available at:

```
https://<username>.github.io/<repo-name>/<tool-name>.html
```

## License

MIT
