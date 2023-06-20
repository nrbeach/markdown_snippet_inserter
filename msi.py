#!/usr/bin/env python3
import ast
import os
import typing as t


def main(args: t.List[str]) -> int:
    for arg in args:
        filename_out = get_output_filename(arg)
        lines = read_template(arg)
        write_rendered_template(lines, filename_out)
    return 0


class NodeTransformer(ast.NodeTransformer):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def visit_Import(self, node: ast.Import) -> t.Any:
        if self.__dict__.__contains__("noimport"):
            return None
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> t.Any:
        if self.__dict__.__contains__("noimport"):
            return None
        return node

    def visit_If(self, node: ast.If) -> t.Any:
        # strips if __name__ == '__main__'
        if self.__dict__.__contains__("noentry"):
            nid = op = value = None
            if node.__dict__.__contains__("test") and isinstance(
                node.__getattribute__("test"), ast.Compare
            ):
                n = node.__getattribute__("test")
                if n.__dict__.__contains__("left") and n.__getattribute__(
                    "left"
                ).__dict__.__contains__("id"):
                    nid = n.__getattribute__("left").__getattribute__("id")
                if (
                    n.__dict__.__contains__("comparators")
                    and len(n.__getattribute__("comparators")) == 1
                    and n.__getattribute__("comparators")[0].__dict__.__contains__(
                        "value"
                    )
                ):
                    value = n.__getattribute__("comparators")[0].__getattribute__(
                        "value"
                    )
                if (
                    n.__dict__.__contains__("ops")
                    and len(n.__getattribute__("ops")) == 1
                ):
                    op = n.__getattribute__("ops")[0]
            if (
                nid
                and op
                and value
                and nid == "__name__"
                and isinstance(op, ast.Eq)
                and value == "__main__"
            ):
                return None
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> t.Any:
        if self.__dict__.__contains__("nomain"):
            if (
                node.__dict__.__contains__("name")
                and node.__dict__.get("name") == "main"
            ):
                return None
        elif self.__dict__.__contains__("func"):
            fn_list = self.__getattribute__("func")
            if (
                node.__dict__.__contains__("name")
                and node.__getattribute__("name") not in fn_list
            ):
                return None
        return node


def read_template(filename: str) -> t.List[str]:
    with open(filename) as fh:
        output = []
        for line in fh.readlines():
            if line.startswith("{{") and line.endswith("}}\n"):
                visitor = get_node_visitor(line)
                source_filename = get_source_filename(line)
                data = read_and_parse_source_file(source_filename, visitor)
                output.extend(data)
            else:
                output.append(line)
    return output


def get_node_visitor(template_str: str) -> ast.NodeTransformer:
    cleaned = template_str.strip("{}\n ")
    opt_dict = {}
    if "|" in cleaned:
        _, options = cleaned.split("|")
        options = options.strip()
        opt_dict.update(**{k: True for k in options.split(" ")})
    elif ":" in cleaned:
        _, functions = cleaned.split(":")
        functions = functions.strip()
        opt_dict.update(
            **{
                "func": [f for f in functions.split(" ")],
                "noimport": True,
                "noentry": True,
            }
        )
    return NodeTransformer(**opt_dict)


def get_source_filename(template_str: str) -> str:
    template_str = template_str.strip("{}\n ")
    if "|" in template_str:
        embedded_file, _ = template_str.split("|")
    elif ":" in template_str:
        embedded_file, _ = template_str.split(":")
    else:
        embedded_file = template_str
    return embedded_file.strip()


def read_and_parse_source_file(
    filename: str, visitor: ast.NodeTransformer
) -> t.List[str]:
    with open(filename) as fh:
        data = fh.read()
        parsed = ast.parse(source=data)
        transformed = visitor.visit(parsed)
        unparsed = ast.unparse(transformed)
        if unparsed[-1] != "\n":
            unparsed += "\n"
        return unparsed.splitlines(keepends=True)


def get_output_filename(filename: str) -> str:
    outfile, _ = os.path.splitext(filename)
    outfile += ".md"
    return outfile


def write_rendered_template(lines: t.List[str], outfile: str) -> None:
    with open(outfile, "w") as fh:
        fh.writelines(lines)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
