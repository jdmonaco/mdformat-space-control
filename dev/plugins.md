---
created: 2025-12-01T08:19:07 (UTC -05:00)
tags: []
source: https://mdformat.readthedocs.io/en/stable/users/plugins.html
author: 
---

# Plugins - mdformat 1.0.0 documentation


Mdformat offers an extensible plugin system for code fence content formatting, Markdown parser extensions (like GFM tables), and modifying/adding other functionality. This document explains how to use plugins. If you want to create a new plugin, refer to the [contributing](https://mdformat.readthedocs.io/en/stable/contributors/contributing.html) docs.

## Code formatter plugins

Mdformat features a plugin system to support formatting of Markdown code blocks where the coding language has been labeled. For instance, if [`mdformat-black`](https://github.com/hukkin/mdformat-black) plugin is installed in the environment, mdformat CLI will automatically format Python code blocks with [Black](https://github.com/psf/black).

For stability, mdformat Python API behavior will not change simply due to a plugin being installed. Code formatters will have to be explicitly enabled in addition to being installed:

```
<span></span><span>import</span><span> </span><span>mdformat</span>

<span>unformatted</span> <span>=</span> <span>"```python</span><span>\n</span><span>'''black converts quotes'''</span><span>\n</span><span>```</span><span>\n</span><span>"</span>
<span># Pass in `codeformatters` here! It is an iterable of coding languages</span>
<span># that should be formatted</span>
<span>formatted</span> <span>=</span> <span>mdformat</span><span>.</span><span>text</span><span>(</span><span>unformatted</span><span>,</span> <span>codeformatters</span><span>=</span><span>{</span><span>"python"</span><span>})</span>
<span>assert</span> <span>formatted</span> <span>==</span> <span>'```python</span><span>\n</span><span>"""black converts quotes"""</span><span>\n</span><span>```</span><span>\n</span><span>'</span>
```

### Existing plugins

This is a curated list of popular code formatter plugins. The list is not exhaustive. Explore mdformat’s [GitHub topic](https://github.com/topics/mdformat) for more.

| Distribution | Supported languages | Notes |
| --- | --- | --- |
| [mdformat-beautysh](https://github.com/hukkin/mdformat-beautysh) | `bash`, `sh` |  |
| [mdformat-black](https://github.com/hukkin/mdformat-black) | `python` |  |
| [mdformat-config](https://github.com/hukkin/mdformat-config) | `json`, `toml`, `yaml` |  |
| [mdformat-gofmt](https://github.com/hukkin/mdformat-gofmt) | `go` | Requires [Go](https://golang.org/doc/install) installation |
| [mdformat-ruff](https://github.com/Freed-Wu/mdformat-ruff) | `python` |  |
| [mdformat-rustfmt](https://github.com/hukkin/mdformat-rustfmt) | `rust` | Requires [rustfmt](https://github.com/rust-lang/rustfmt#quick-start) installation |
| [mdformat-shfmt](https://github.com/hukkin/mdformat-shfmt) | `bash`, `sh` | Requires either [shfmt](https://github.com/mvdan/sh#shfmt), [Docker](https://docs.docker.com/get-docker/) or [Podman](https://podman.io/docs/installation) installation |
| [mdformat-web](https://github.com/hukkin/mdformat-web) | `javascript`, `js`, `css`, `html`, `xml` |  |

## Parser extension plugins

By default, mdformat only parses and renders [CommonMark](https://spec.commonmark.org/current/). Installed plugins can add extensions to the syntax, such as footnotes, tables, and other document elements.

For stability, mdformat Python API behavior will not change simply due to a plugin being installed. Extensions will have to be explicitly enabled in addition to being installed:

```
<span></span><span>import</span><span> </span><span>mdformat</span>

<span>unformatted</span> <span>=</span> <span>"content...</span><span>\n</span><span>"</span>
<span># Pass in `extensions` here! It is an iterable of extensions that should be loaded</span>
<span>formatted</span> <span>=</span> <span>mdformat</span><span>.</span><span>text</span><span>(</span><span>unformatted</span><span>,</span> <span>extensions</span><span>=</span><span>{</span><span>"tables"</span><span>})</span>
```

### Existing plugins

This is a curated list of popular parser extension plugins. The list is not exhaustive. Explore mdformat’s [GitHub topic](https://github.com/topics/mdformat) for more.

| Distribution | Plugins | Description |
| --- | --- | --- |
| [mdformat-admon](https://github.com/KyleKing/mdformat-admon) | `admon` | Adds support for [python-markdown](https://python-markdown.github.io/extensions/admonition/) admonitions |
| [mdformat-deflist](https://github.com/executablebooks/mdformat-deflist) | `deflist` | Adds support for [Pandoc-style](https://pandoc.org/MANUAL.html#definition-lists) definition lists |
| [mdformat-footnote](https://github.com/executablebooks/mdformat-footnote) | `footnote` | Adds support for [Pandoc-style](https://pandoc.org/MANUAL.html#footnotes) footnotes |
| [mdformat-frontmatter](https://github.com/butler54/mdformat-frontmatter) | `frontmatter` | Adds support for front matter, and formats YAML front matter |
| [mdformat-gfm](https://github.com/hukkin/mdformat-gfm) | `gfm`, `tables` | Changes target specification to GitHub Flavored Markdown (GFM) |
| [mdformat-gfm-alerts](https://github.com/KyleKing/mdformat-gfm-alerts) | `gfm_alerts` | Extends GitHub Flavored Markdown (GFM) with "Alerts" |
| [mdformat-mkdocs](https://github.com/KyleKing/mdformat-mkdocs) | `mkdocs` | Changes target specification to MKDocs. Indents lists with 4-spaces instead of 2 |
| [mdformat-myst](https://github.com/executablebooks/mdformat-myst) | `myst` | Changes target specification to [MyST](https://myst-parser.readthedocs.io/en/latest/using/syntax.html) |
| [mdformat-toc](https://github.com/hukkin/mdformat-toc) | `toc` | Adds the capability to auto-generate a table of contents |

## Other misc plugins

### Existing plugins

This is a curated list of other plugins that don’t fit the above categories. The list is not exhaustive. Explore mdformat’s [GitHub topic](https://github.com/topics/mdformat) for more.

| Distribution | Plugins | Description |
| --- | --- | --- |
| [mdformat-pyproject](https://github.com/csala/mdformat-pyproject) | `pyproject` | Adds support for loading options from a `[tool.mdformat]` section inside the `pyproject.toml` file, if it exists |
| [mdformat-simple-breaks](https://github.com/csala/mdformat-simple-breaks) | `simple_breaks` | Render [thematic breaks](https://mdformat.readthedocs.io/en/stable/users/style.html#thematic-breaks) using three dashes instead of 70 underscores |
