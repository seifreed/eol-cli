"""Unit tests for the _output module (emit, validate_format_options)."""

from unittest.mock import MagicMock

import click
import pytest

from eol_cli.commands._output import emit, validate_format_options


class TestValidateFormatOptions:
    """Test validate_format_options."""

    def test_json_only_passes(self):
        validate_format_options(output_json=True, output_xml=False)

    def test_xml_only_passes(self):
        validate_format_options(output_json=False, output_xml=True)

    def test_neither_passes(self):
        validate_format_options(output_json=False, output_xml=False)

    def test_both_raises_usage_error(self):
        with pytest.raises(click.UsageError, match="mutually exclusive"):
            validate_format_options(output_json=True, output_xml=True)


class TestEmit:
    """Test emit function dispatch."""

    def test_emit_json(self, capsys):
        data = {"key": "value"}
        emit(data, output_json=True, output_xml=False)
        captured = capsys.readouterr()
        assert '"key"' in captured.out
        assert '"value"' in captured.out

    def test_emit_xml(self, capsys):
        data = {"key": "value"}
        emit(data, output_json=False, output_xml=True)
        captured = capsys.readouterr()
        assert "<key>" in captured.out
        assert "value" in captured.out

    def test_emit_rich_calls_rich_fn(self):
        rich_fn = MagicMock()
        data = {"key": "value"}
        emit(data, output_json=False, output_xml=False, rich_fn=rich_fn, extra="kwarg")
        rich_fn.assert_called_once_with(data, extra="kwarg")

    def test_emit_rich_fn_not_called_for_json(self):
        rich_fn = MagicMock()
        emit({"k": "v"}, output_json=True, output_xml=False, rich_fn=rich_fn)
        rich_fn.assert_not_called()

    def test_emit_rich_fn_not_called_for_xml(self):
        rich_fn = MagicMock()
        emit({"k": "v"}, output_json=False, output_xml=True, rich_fn=rich_fn)
        rich_fn.assert_not_called()

    def test_emit_without_rich_fn_for_json(self, capsys):
        """emit() works without rich_fn when using JSON output."""
        emit({"k": "v"}, output_json=True, output_xml=False)
        captured = capsys.readouterr()
        assert '"k"' in captured.out

    def test_emit_without_rich_fn_raises_for_rich(self):
        """emit() raises ValueError when rich_fn is None and no format flag is set."""
        with pytest.raises(ValueError, match="rich_fn is required"):
            emit({"k": "v"}, output_json=False, output_xml=False)
