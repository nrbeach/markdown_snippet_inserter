# Markdown Snipper Inserter

---

A super simple Python snippet inserter.

## Usage

Create a markdown file `foo.mdt` and add in a code block as below, containing a tag specifying the python file to source and any option:

`````markdown
# Heading

---

```python
{{ path/to/your_file.py | option_a option_b }}
```
`````

Run `msi.py`:

`# ./msi.py path/to/foo.mdt`

This will then create a rendered markdown file `path/to/foo.md`

---

### Options

Various elements and code blocks can be excluded using the following tags. Exclusionary tags must use be specified by `|` operator.

`{{ filename.py | <noimport|noentry|nomain> }}`

* `noimport` Strips all import statements.
* `noentry` Removes `if __name__ == "__main__"` entrypoint.
* `nomain` Removes the `main` function often used for testing/validation.

---

One or more functions can be displayed using the colon `:` operator. This implicitly removes the `main` function (if not specified), any imports, and the entrypoint.

`{{ filename.py : function_a function_b }}`
