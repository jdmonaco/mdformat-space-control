---
created: 2025-12-01T08:18:37 (UTC -05:00)
tags: []
source: https://mdformat.readthedocs.io/en/stable/index.html
author: 
---

# mdformat 1.0.0 documentation


## 

> CommonMark compliant Markdown formatter

Mdformat is an opinionated Markdown formatter that can be used to enforce a consistent style in Markdown files. Mdformat is a Unix-style command-line tool as well as a Python library.

The features/opinions of the formatter include:

-   Consistent indentation and whitespace across the board
    
-   Always use ATX style headings
    
-   Move all link references to the bottom of the document (sorted by label)
    
-   Reformat indented code blocks as fenced code blocks
    
-   Use `1.` as the ordered list marker if possible, also for noninitial list items
    

Mdformat will not change word wrapping by default. The rationale for this is to support [Semantic Line Breaks](https://sembr.org/).

For a comprehensive description and rationalization of the style, read [the style guide](https://mdformat.readthedocs.io/en/stable/users/style.html).

## Frequently Asked Questions

### Why does mdformat backslash escape special syntax specific to MkDocs / Hugo / Obsidian / GitHub / some other Markdown engine?

Mdformat is a CommonMark formatter. It doesn’t have out-of-the-box support for syntax other than what is defined in [the CommonMark specification](https://spec.commonmark.org/current/).

The custom syntax that these Markdown engines introduce typically redefines the meaning of angle brackets, square brackets, parentheses, hash character — characters that are special in CommonMark. Mdformat often resorts to backslash escaping these characters to ensure its formatting changes never alter a rendered document.

Additionally some engines, namely MkDocs, [do not support](https://github.com/mkdocs/mkdocs/issues/1835) CommonMark to begin with, so incompatibilities are unavoidable.

Luckily mdformat is extensible by plugins. For many Markdown engines you’ll find support by searching [the plugin docs](https://mdformat.readthedocs.io/en/stable/users/plugins.html) or [mdformat GitHub topic](https://github.com/topics/mdformat).

You may also want to consider a documentation generator that adheres to CommonMark as its base syntax e.g. [mdBook](https://rust-lang.github.io/mdBook/) or [Sphinx with Markdown](https://www.sphinx-doc.org/en/master/usage/markdown.html).

### Why not use [Prettier](https://github.com/prettier/prettier) instead?

Mdformat is pure Python code! Python is pre-installed on macOS and virtually any Linux distribution, meaning that typically little to no additional installations are required to run mdformat. This argument also holds true when using together with [pre-commit](https://github.com/pre-commit/pre-commit) (also Python). Prettier on the other hand requires Node.js/npm.

Prettier suffers from [numerous](https://github.com/prettier/prettier/issues?q=is%3Aopen+label%3Alang%3Amarkdown+label%3Atype%3Abug+) bugs, many of which cause changes in Markdown AST and rendered HTML. Many of these bugs are a consequence of using [`remark-parse`](https://github.com/remarkjs/remark/tree/main/packages/remark-parse) v8.x as Markdown parser which, according to the author themselves, is [inferior to markdown-it](https://github.com/remarkjs/remark/issues/75#issuecomment-143532326) used by mdformat. `remark-parse` v9.x is advertised as CommonMark compliant and presumably would fix many of the issues, but is not used by Prettier (v3.3.3) yet.

Prettier (v3.3.3), being able to format many languages other than Markdown, is a large package with 73 direct dependencies (mdformat only has one in Python 3.11+). This can be a disadvantage in many environments, one example being size optimized Docker images.

Mdformat’s parser extension plugin API allows not only customization of the Markdown specification in use, but also advanced features like [automatic table of contents generation](https://github.com/hukkin/mdformat-toc). Also provided is a code formatter plugin API enabling integration of embedded code formatting for any programming language.

### What’s wrong with the mdformat logo? It renders incorrectly and is just terrible in general.

Nope, the logo is actually pretty great – you’re terrible. The logo is more a piece of art than a logo anyways, depicting the horrors of poorly formatted text documents. I made it myself!

That said, if you have any graphic design skills and want to contribute a revised version, a PR is more than welcome 😄.
