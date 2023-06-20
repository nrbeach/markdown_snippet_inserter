import ast

import pytest

from msi import get_node_visitor
from msi import get_source_filename
from msi import NodeTransformer
from msi import read_and_parse_source_file
from msi import read_template


@pytest.fixture
def code_block():
    code = """
import a
import b
import c

def main(args):
    print(len(args))
    return 0

def __name__func(a):
    return a + 1

def import_func(b):
    return b + 2

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
"""
    return code


@pytest.mark.parametrize(
    "opts, removed, expected",
    [
        (
            {},
            [],
            [
                "def __name__func(a):",
                "def import_func(b):",
                "import a",
                "if __name__ == '__main__':",
                "def main(args):",
            ],
        ),
        (
            {"noimport": True},
            ["import a"],
            [
                "def __name__func(a):",
                "def import_func(b):",
                "if __name__ == '__main__':",
                "def main(args):",
            ],
        ),
        (
            {"noentry": True},
            ["if __name__ == '__main__':"],
            [
                "def __name__func(a):",
                "def import_func(b):",
                "import a",
                "def main(args):",
            ],
        ),
        (
            {"nomain": True},
            ["def main(args):"],
            [
                "def __name__func(a):",
                "def import_func(b):",
                "import a",
                "if __name__ == '__main__':",
            ],
        ),
        (
            {"noimport": True, "nomain": True},
            ["import a", "def main(args):"],
            [
                "def __name__func(a):",
                "def import_func(b):",
                "if __name__ == '__main__':",
            ],
        ),
        (
            {"noimport": True, "noentry": True},
            ["import a", "if __name__ == '__main__':"],
            ["def __name__func(a):", "def import_func(b):", "def main(args):"],
        ),
        (
            {"noentry": True, "nomain": True},
            ["if __name__ == '__main__':", "def main(args):"],
            ["def __name__func(a):", "def import_func(b):", "import a"],
        ),
        (
            {"noimport": True, "noentry": True, "nomain": True},
            ["import a", "if __name__ == '__main__':", "def main(args):"],
            ["def __name__func(a):", "def import_func(b):"],
        ),
    ],
)
def test_node_transformer_removes(code_block, opts, removed, expected):
    visitor = NodeTransformer(**opts)
    parsed = ast.parse(source=code_block)
    transformed = visitor.visit(parsed)
    code = ast.unparse(transformed)
    split = code.splitlines(keepends=False)
    for item in removed:
        assert item not in split
    for item in expected:
        assert item in split


@pytest.mark.parametrize(
    "opts, removed, expected",
    [
        (
            {"func": ["__name__func"]},
            [
                "def import_func(b):",
                "import a",
                "if __name__ == '__main__':",
                "def main(args):",
            ],
            ["def __name__func(a):"],
        ),
        (
            {"func": ["import_func"]},
            [
                "def __name_func(a):",
                "import a",
                "if __name__ == '__main__':",
                "def main(args):",
            ],
            ["def import_func(b):"],
        ),
        (
            {"func": ["__name__func", "import_func"]},
            ["import a", "if __name__ == '__main__':", "def main(args):"],
            ["def __name__func(a):", "def import_func(b):"],
        ),
        (
            {"func": ["__name__func", "main"]},
            ["def import_func(b):", "import a", "if __name__ == '__main__':"],
            ["def __name__func(a):", "def main(args):"],
        ),
        (
            {"func": ["import_func", "main"]},
            ["def __name_func(a):", "import a", "if __name__ == '__main__':"],
            ["def import_func(b):", "def main(args):"],
        ),
        (
            {"func": ["__name_func", "import_func", "main"]},
            ["import a", "if __name__ == '__main__':"],
            ["def __name_func(a):", "def import_func(b):", "def main(args):"],
        ),
    ],
)
def test_node_transformer_isolates(code_block, opts, removed, expected):
    opts.update(**{"noimport": True, "noentry": True})
    visitor = NodeTransformer(**opts)
    parsed = ast.parse(source=code_block)
    transformed = visitor.visit(parsed)
    code = ast.unparse(transformed)
    split = code.splitlines(keepends=False)
    for item in removed:
        assert item not in split
    for item in expected:
        assert item in expected


@pytest.mark.parametrize(
    "template_str, opts",
    [
        ("{{ foo.py | noimport }}", {"noimport": True}),
        ("{{ foo.py | noentry }}", {"noentry": True}),
        ("{{ foo.py | nomain }}", {"nomain": True}),
        (
            "{{ foo.py : import_func}}",
            {"func": ["import_func"], "noentry": True, "noimport": True},
        ),
        (
            "{{ foo.py : import_func main}}",
            {"func": ["import_func", "main"], "noentry": True, "noimport": True},
        ),
        ("{{ foo.py }}", {}),
    ],
)
def test_get_node_visitor(template_str, opts):
    visitor = get_node_visitor(template_str)
    for k, v in opts.items():
        assert visitor.__getattribute__(k) == v


@pytest.mark.parametrize(
    "template_str, filename",
    [
        ("{{ foo.py | noimport }}", "foo.py"),
        ("{{ foo.py : noentry }}", "foo.py"),
        ("{{ foo.py }}", "foo.py"),
    ],
)
def test_get_source_filename(template_str, filename):
    assert get_source_filename(template_str) == filename
