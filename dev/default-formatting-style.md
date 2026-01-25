---
created: 2025-12-01T08:19:20 (UTC -05:00)
tags: []
source: https://mdformat.readthedocs.io/en/stable/users/style.html
author: 
---

# Formatting style - mdformat 1.0.0 documentation


This document describes, demonstrates, and rationalizes the formatting style that mdformat follows.

Mdformat’s formatting style is crafted so that writing, editing and collaborating on Markdown documents is as smooth as possible. The style is consistent, and minimizes diffs (for ease of reviewing changes), sometimes at the cost of some readability.

Mdformat makes sure to only change style, not content. Once converted to HTML and rendered on screen, formatted Markdown should yield a result that is visually identical to the unformatted document. Mdformat CLI includes a safety check that will error and refuse to apply changes to a file if Markdown AST is not equal before and after formatting.

## Headings

For consistency, only ATX headings are used. Setext headings are reformatted using the ATX style. ATX headings are used because they can be consistently used for any heading level, whereas setext headings only allow level 1 and 2 headings.

Input:

```
<span></span><span>First level heading</span>
<span>===</span>

<span>Second level heading</span>
<span>---</span>
```

Output:

```
<span></span><span># First level heading</span>

<span>## Second level heading</span>
```

## Bullet lists

Mdformat uses `-` as the bullet list marker. In the case of consecutive bullet lists, mdformat alternates between `-` and `*` markers.

## Ordered lists

Mdformat uses `.` as ordered list marker type. In the case of consecutive ordered lists, mdformat alternates between `.` and `)` types.

Mdformat uses `1.` or `1)` as the ordered list marker, also for noninital list items.

Input:

```
<span></span><span>1.</span> Item A
<span>2.</span> Item B
<span>3.</span> Item C
```

Output:

```
<span></span><span>1.</span> Item A
<span>1.</span> Item B
<span>1.</span> Item C
```

This “non-numbering” style was chosen to minimize diffs. But how exactly? Lets imagine we are listing the alphabets, using a proper consecutive numbering style:

Now we notice an error was made, and that the first character “a” is missing. We add it as the first item in the list. As a result, the numbering of every subsequent item in the list will increase by one, meaning that the diff will touch every line in the list. The non-numbering style solves this issue: only the added line will show up in the diff.

Mdformat allows consecutive numbering via configuration.

## Code blocks

Only fenced code blocks are allowed. Indented code blocks are reformatted as fenced code blocks.

Fenced code blocks are preferred because they allow setting an info string, which indented code blocks do not support.

## Code spans

Length of a code span starting/ending backtick string is reduced to minimum. Needless space characters are stripped from the front and back, unless the content contains backticks.

Input:

`````
<span></span>````Backtick string is reduced.````

<span>` Space is stripped from the front and back... `</span>

```` ...unless a "<span>`" character is present. `</span>```
`````

Output:

```
<span></span><span>`Backtick string is reduced.`</span>

<span>`Space is stripped from the front and back...`</span>

`` ...unless a "<span>`" character is present. `</span>`
```

## Inline links

Redundant angle brackets surrounding a link destination will be removed.

Input:

```
<span></span>[<span>Python</span>](<span>&lt;https://python.org&gt;</span>)
```

Output:

```
<span></span>[<span>Python</span>](<span>https://python.org</span>)
```

## Reference links

All link reference definitions are moved to the bottom of the document, sorted by label. Unused and duplicate references are removed.

Input:

```
<span></span>[<span>dupe ref</span>]: <span>https://gitlab.com</span>
[<span>dupe ref</span>]: <span>link1</span>
[<span>unused ref</span>]: <span>link2</span>

Here's a link to [<span>GitLab</span>][<span>dupe ref</span>]
```

Output:

```
<span></span>Here's a link to [<span>GitLab</span>][<span>dupe ref</span>]

[<span>dupe ref</span>]: <span>https://gitlab.com</span>
```

## Paragraph word wrapping

Mdformat by default will not change word wrapping. The rationale for this is to encourage and support [Semantic Line Breaks](https://sembr.org/), a technique described by Brian Kernighan in the early 1970s, yet still as relevant as ever today:

> **Hints for Preparing Documents**
> 
> Most documents go through several versions (always more than you expected) before they are finally finished. Accordingly, you should do whatever possible to make the job of changing them easy.
> 
> First, when you do the purely mechanical operations of typing, type so subsequent editing will be easy. Start each sentence on a new line. Make lines short, and break lines at natural places, such as after commas and semicolons, rather than randomly. Since most people change documents by rewriting phrases and adding, deleting and rearranging sentences, these precautions simplify any editing you have to do later.
> 
> _— Brian W. Kernighan. “UNIX for Beginners”. 1974_

Mdformat allows removing word wrap or setting a target wrap width via configuration.

## Thematic breaks

Thematic breaks are formatted as a 70 character wide string of underscores. A wide thematic break is distinguishable, and visually resembles how a corresponding HTML `<hr>` tag is typically rendered.

## Whitespace

Mdformat applies consistent whitespace across the board:

-   Convert line endings to a single newline character
    
-   Strip paragraph trailing and leading whitespace
    
-   Indent contents of block quotes and list items consistently
    
-   Always separate blocks with a single empty line (an exception being tight lists where the separator is a single newline character)
    
-   Always end the document in a single newline character (an exception being an empty document)
    

## Hard line breaks

Hard line breaks are always a backslash preceding a line ending. The alternative syntax, two or more spaces before a line ending, is not used because it is not visible.

Input:

```
<span></span>Hard line break is here:   
Can you see it?
```

Output:

```
<span></span>Hard line break is here:\
Can you see it?
```
