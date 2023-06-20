# Markdown Snipper Inserter

---

A super simple Python snippet inserter.

I wrote this to insert Python source examples into Markdown documents for my personal interview study guide/notes.

## Usage

Create a Markdown file `foo.mdt` using the usual schema. In the desired codeblock, add a tag specifying the python file
to source and any option:

`````markdown
# Blah blah blah

```python
{{ path/to/your_file.py | option_a option_b }}
```
`````

Run markdown snippet inserter and provide the templated filename:

`# ./msi.py path/to/foo.mdt`

This will then create a rendered markdown file `path/to/foo.md`.

---

## Options

With no options specified, markdown snippet inserter will render the entire source file.

### Exclusionary Options

Various elements and code blocks can be excluded using the following tags. Exclusionary tags must use be specified by
the `|` operator.

`{{ filename.py | <noimport|noentry|nomain> }}`

* `noimport` Strips all import statements.
* `noentry` Removes `if __name__ == "__main__"` entrypoint.
* `nomain` Removes the `main` function often used for testing/validation.


### Specifying Function(s)
One or more functions can be displayed using the colon `:` operator. This implicitly removes the `main` function
(if not otherwise specified), any imports, and the entrypoint.

`{{ filename.py : function_a function_b }}`


## Contributing

If you find this useful and wish to extend it, please fork the repo, add your changes and appropriate tests, and open a
PR.
