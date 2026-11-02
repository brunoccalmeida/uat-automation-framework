"""Steps keep page objects in local variables, never on the behave context.

A page object is a thin wrapper around the driver; the real state lives in the
browser. Kept on ``context``, it outlives the page it describes and the next
step can read a page the browser already left.
"""

import ast
from pathlib import Path


def _context_page_attributes(source: str) -> list[tuple[int, str]]:
    """Return (line, name) of every ``context.<name>_page`` access."""
    return [
        (node.lineno, node.attr)
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "context"
        and (node.attr == "page" or node.attr.endswith("_page"))
    ]


def test_detects_context_page_reads_and_writes():
    """Should flag both storing and reading a page on the context."""
    source = "context.cart_page = CartPage(d)\ncontext.page.click()\n"

    assert _context_page_attributes(source) == [(1, "cart_page"), (2, "page")]


def test_ignores_scenario_data_and_local_pages():
    """Should allow scenario data on the context and pages in local variables."""
    source = "context.first_product = name\npage = CartPage(context.driver)\n"

    assert not _context_page_attributes(source)


def test_steps_do_not_keep_page_objects_on_context():
    """No module under features/ keeps a page object on the context."""
    offenders = [
        f"{path}:{line} context.{name}"
        for path in Path("features").rglob("*.py")
        for line, name in _context_page_attributes(path.read_text(encoding="utf-8"))
    ]

    assert not offenders, "Use a local page object instead:\n" + "\n".join(offenders)
