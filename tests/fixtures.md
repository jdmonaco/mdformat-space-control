basic tight list
.
- item1

- item2

- item3
.
- item1
- item2
- item3
.

numbered tight list
.
1. first

2. second

3. third
.
1. first
2. second
3. third
.

mixed markers preserved
.
- item1
- item2

* item3
* item4
.
- item1
- item2

* item3
* item4
.

list after paragraph
.
Some text here.

- item1

- item2
.
Some text here.

- item1
- item2
.

paragraph after list
.
- item1

- item2

Some text here.
.
- item1
- item2

Some text here.
.

nested lists with alternating markers
.
- Outer 1
  * Inner 1
  * Inner 2
- Outer 2
  * Inner 3
  * Inner 4
.
- Outer 1
  - Inner 1
  - Inner 2
- Outer 2
  - Inner 3
  - Inner 4
.

multiple list types
.
Some intro text.

- List 1 item 1

- List 1 item 2

* List 2 item 1

* List 2 item 2

1. Numbered item 1

2. Numbered item 2
.
Some intro text.

- List 1 item 1
- List 1 item 2

* List 2 item 1
* List 2 item 2

1. Numbered item 1
2. Numbered item 2
.

complex nested structure
.
1. First ordered item
   - Nested unordered
   - Another nested
2. Second ordered item
   * Different marker
   * Maintains structure
.
1. First ordered item
  - Nested unordered
  - Another nested
2. Second ordered item
  - Different marker
  - Maintains structure
.

list with blank lines in items
.
- First item with multiple paragraphs

  Second paragraph of first item

- Second item
.
- First item with multiple paragraphs

  Second paragraph of first item

- Second item
.

empty list items
.
- First item
- 
- Third item
.
- First item
-
- Third item
.

mixed single and multi paragraph items
.
- Simple item 1

- Item with multiple paragraphs

  Second paragraph here

- Simple item 2
.
- Simple item 1

- Item with multiple paragraphs

  Second paragraph here

- Simple item 2
.

basic checkbox list
.
- [ ] Task 1

- [x] Task 2

- [ ] Task 3
.
- [ ] Task 1
- [x] Task 2
- [ ] Task 3
.

nested checkbox list
.
- [ ] Parent task 1
  - [x] Completed subtask
  - [ ] Pending subtask
- [x] Parent task 2
.
- [ ] Parent task 1
  - [x] Completed subtask
  - [ ] Pending subtask
- [x] Parent task 2
.

mixed checkbox and regular items
.
- [ ] Task item

- Regular item

- [x] Completed task
.
- [ ] Task item
- Regular item
- [x] Completed task
.

checkbox with continuation
.
- [ ] Task with
  continuation text
- [x] Another task
.
- [ ] Task with\
  continuation text
- [x] Another task
.

multi-paragraph checkbox item
.
- [ ] Task with paragraphs

  Second paragraph here.

- [x] Simple task
.
- [ ] Task with paragraphs

  Second paragraph here.

- [x] Simple task
.

normal link unchanged
.
[normal link](https://example.com)
.
[normal link](https://example.com)
.

link in paragraph
.
Check [this link](https://example.com) for info.
.
Check [this link](https://example.com) for info.
.