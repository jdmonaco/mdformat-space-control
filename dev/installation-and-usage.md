---
created: 2025-12-01T08:19:48 (UTC -05:00)
tags: []
source: https://mdformat.readthedocs.io/en/stable/users/installation_and_usage.html
author: 
---

# Installation and usage - mdformat 1.0.0 documentation


## Installing

Install with [CommonMark](https://spec.commonmark.org/current/) support:

Install with [GitHub Flavored Markdown (GFM)](https://github.github.com/gfm/) support:

```
<span></span>pipx<span> </span>install<span> </span>mdformat
pipx<span> </span>inject<span> </span>mdformat<span> </span>mdformat-gfm
```

Note that GitHub’s Markdown renderer supports syntax extensions not included in the GFM specification. For full GitHub support do:

```
<span></span>pipx<span> </span>install<span> </span>mdformat
pipx<span> </span>inject<span> </span>mdformat<span> </span>mdformat-gfm<span> </span>mdformat-frontmatter<span> </span>mdformat-footnote<span> </span>mdformat-gfm-alerts
```

Install with [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/using/syntax.html) support:

```
<span></span>pipx<span> </span>install<span> </span>mdformat
pipx<span> </span>inject<span> </span>mdformat<span> </span>mdformat-myst
```

Warning

The formatting style produced by mdformat may change in each version. It is recommended to pin mdformat dependency version.

## Command line usage

### Format files

Format files `README.md` and `CHANGELOG.md` in place

```
<span></span>mdformat<span> </span>README.md<span> </span>CHANGELOG.md
```

Format `.md` files in current working directory recursively

Read Markdown from standard input until `EOF`. Write formatted Markdown to standard output.

### Check formatting

```
<span></span>mdformat<span> </span>--check<span> </span>README.md<span> </span>CHANGELOG.md
```

This will not apply any changes to the files. If a file is not properly formatted, the exit code will be non-zero.

### Options

```
<span></span><span>foo@bar:~$ </span>mdformat<span> </span>--help
<span>usage: mdformat [-h] [--check] [--no-validate] [--version] [--number]</span>
<span>                [--wrap {keep,no,INTEGER}] [--end-of-line {lf,crlf,keep}]</span>
<span>                [--exclude PATTERN] [--extensions EXTENSION]</span>
<span>                [--codeformatters LANGUAGE]</span>
<span>                [paths ...]</span>

<span>CommonMark compliant Markdown formatter</span>

<span>positional arguments:</span>
<span>  paths                 files to format</span>

<span>options:</span>
<span>  -h, --help            show this help message and exit</span>
<span>  --check               do not apply changes to files</span>
<span>  --no-validate         do not validate that the rendered HTML is consistent</span>
<span>  --version             show program's version number and exit</span>
<span>  --number              apply consecutive numbering to ordered lists</span>
<span>  --wrap {keep,no,INTEGER}</span>
<span>                        paragraph word wrap mode (default: keep)</span>
<span>  --end-of-line {lf,crlf,keep}</span>
<span>                        output file line ending mode (default: lf)</span>
<span>  --exclude PATTERN     exclude files that match the Unix-style glob pattern</span>
<span>                        (multiple allowed)</span>
<span>  --extensions EXTENSION</span>
<span>                        require and enable an extension plugin (multiple</span>
<span>                        allowed) (use `--no-extensions` to disable) (default:</span>
<span>                        all enabled)</span>
<span>  --codeformatters LANGUAGE</span>
<span>                        require and enable a code formatter plugin (multiple</span>
<span>                        allowed) (use `--no-codeformatters` to disable)</span>
<span>                        (default: all enabled)</span>
```

The `--exclude` option is only available on Python 3.13+.

## Python API usage

### Format text

```
<span></span><span>import</span><span> </span><span>mdformat</span>

<span>unformatted</span> <span>=</span> <span>"</span><span>\n\n</span><span># A header</span><span>\n\n</span><span>"</span>
<span>formatted</span> <span>=</span> <span>mdformat</span><span>.</span><span>text</span><span>(</span><span>unformatted</span><span>)</span>
<span>assert</span> <span>formatted</span> <span>==</span> <span>"# A header</span><span>\n</span><span>"</span>
```

### Format a file

Format file `README.md` in place:

```
<span></span><span>import</span><span> </span><span>mdformat</span>

<span># Input filepath as a string...</span>
<span>mdformat</span><span>.</span><span>file</span><span>(</span><span>"README.md"</span><span>)</span>

<span># ...or a pathlib.Path object</span>
<span>import</span><span> </span><span>pathlib</span>

<span>filepath</span> <span>=</span> <span>pathlib</span><span>.</span><span>Path</span><span>(</span><span>"README.md"</span><span>)</span>
<span>mdformat</span><span>.</span><span>file</span><span>(</span><span>filepath</span><span>)</span>
```

### Options

All formatting style modifying options available in the CLI are also available in the Python API, with equivalent option names:

```
<span></span><span>import</span><span> </span><span>mdformat</span>

<span>mdformat</span><span>.</span><span>file</span><span>(</span>
    <span>"FILENAME.md"</span><span>,</span>
    <span>options</span><span>=</span><span>{</span>
        <span>"number"</span><span>:</span> <span>True</span><span>,</span>  <span># switch on consecutive numbering of ordered lists</span>
        <span>"wrap"</span><span>:</span> <span>60</span><span>,</span>  <span># set word wrap width to 60 characters</span>
    <span>}</span>
<span>)</span>
```

## Usage as a pre-commit hook

`mdformat` can be used as a [pre-commit](https://github.com/pre-commit/pre-commit) hook. Add the following to your project’s `.pre-commit-config.yaml` to enable this:

```
<span></span><span>-</span><span> </span><span>repo</span><span>:</span><span> </span><span>https://github.com/hukkin/mdformat</span>
<span>  </span><span>rev</span><span>:</span><span> </span><span>1.0.0</span><span>  </span><span># Use the ref you want to point at</span>
<span>  </span><span>hooks</span><span>:</span>
<span>  </span><span>-</span><span> </span><span>id</span><span>:</span><span> </span><span>mdformat</span>
<span>    </span><span># Optionally add plugins</span>
<span>    </span><span>additional_dependencies</span><span>:</span>
<span>    </span><span>-</span><span> </span><span>mdformat-gfm</span>
<span>    </span><span>-</span><span> </span><span>mdformat-black</span>
```
