"""Unit tests for the _output module (emit, validate_format_options)."""

from unittest.mock import MagicMock

import click
import pytest

from eol_cli.commands._output import emit, validate_format_options


class TestValidateFormatOptions:
    """Test validate_format_options."""

    def test_json_only_passes(self):
        validate_format_options(output_json=True, output_xml=False, output_sarif=False)

    def test_xml_only_passes(self):
        validate_format_options(output_json=False, output_xml=True, output_sarif=False)

    def test_sarif_only_passes(self):
        validate_format_options(output_json=False, output_xml=False, output_sarif=True)

    def test_neither_passes(self):
        validate_format_options(output_json=False, output_xml=False, output_sarif=False)

    def test_json_xml_raises(self):
        with pytest.raises(click.UsageError, match="mutually exclusive"):
            validate_format_options(output_json=True, output_xml=True, output_sarif=False)

    def test_json_sarif_raises(self):
        with pytest.raises(click.UsageError, match="mutually exclusive"):
            validate_format_options(output_json=True, output_xml=False, output_sarif=True)

    def test_xml_sarif_raises(self):
        with pytest.raises(click.UsageError, match="mutually exclusive"):
            validate_format_options(output_json=False, output_xml=True, output_sarif=True)

    def test_all_three_raises(self):
        with pytest.raises(click.UsageError, match="mutually exclusive"):
            validate_format_options(output_json=True, output_xml=True, output_sarif=True)


class TestEmit:
    """Test emit function dispatch."""

    def test_emit_json(self, capsys):
        data = {"key": "value"}
        rich_fn = MagicMock()
        emit(data, output_json=True, output_xml=False, rich_fn=rich_fn)
        captured = capsys.readouterr()
        assert '"key"' in captured.out
        rich_fn.assert_not_called()

    def test_emit_xml(self, capsys):
        data = {"key": "value"}
        rich_fn = MagicMock()
        emit(data, output_json=False, output_xml=True, rich_fn=rich_fn)
        captured = capsys.readouterr()
        assert "<key>" in captured.out
        rich_fn.assert_not_called()

    def test_emit_sarif(self, capsys):
        data = {"result": []}
        rich_fn = MagicMock()
        emit(data, output_json=False, output_xml=False, rich_fn=rich_fn, output_sarif=True)
        captured = capsys.readouterr()
        assert '"version": "2.1.0"' in captured.out
        rich_fn.assert_not_called()

    def test_emit_rich_calls_rich_fn(self):
        rich_fn = MagicMock()
        data = {"key": "value"}
        emit(data, output_json=False, output_xml=False, rich_fn=rich_fn, extra="kwarg")
        rich_fn.assert_called_once_with(data, extra="kwarg")
