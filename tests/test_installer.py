"""
tests/test_installer.py
Unit tests for the idempotent installer utilities.
"""
from residue.installer.utils import replace_or_append_section

_MARKER = "## residue"
_END = "<!-- residue-end -->"

INSTRUCTION = """## residue

You are connected to residue via MCP.
"""


def test_append_when_not_present():
    content = "# Existing content\n\nSome other rules.\n"
    result = replace_or_append_section(content, INSTRUCTION)
    assert _MARKER in result
    assert _END in result
    assert "Existing content" in result


def test_idempotent_on_second_call():
    content = "# Rules\n"
    first = replace_or_append_section(content, INSTRUCTION)
    second = replace_or_append_section(first, INSTRUCTION)
    # Should not duplicate the section
    assert second.count(_MARKER) == 1


def test_updates_existing_section():
    content = f"# Rules\n\n## residue\n\nOLD CONTENT\n{_END}\n"
    new_instruction = "## residue\n\nNEW CONTENT\n"
    result = replace_or_append_section(content, new_instruction)
    assert "NEW CONTENT" in result
    assert "OLD CONTENT" not in result
