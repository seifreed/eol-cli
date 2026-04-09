"""Unit tests for the _output module (emit, validate_format_options)."""

from unittest.mock import MagicMock

import click
import pytest

from eol_cli.commands._output import emit, validate_format_options
from eol_cli.presentation.responses import ApiResponse


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
        data = {"schema_version": "1.2.0", "result": {"key": "value"}}
        rich_fn = MagicMock()
        emit(data, output_json=True, output_xml=False, rich_fn=rich_fn)
        captured = capsys.readouterr()
        if '"key"' not in captured.out:
            raise AssertionError
        rich_fn.assert_not_called()

    def test_emit_xml(self, capsys):
        data = {"schema_version": "1.2.0", "result": {"key": "value"}}
        rich_fn = MagicMock()
        emit(data, output_json=False, output_xml=True, rich_fn=rich_fn)
        captured = capsys.readouterr()
        if "<key>" not in captured.out:
            raise AssertionError
        rich_fn.assert_not_called()

    def test_emit_sarif(self, capsys):
        data = {"schema_version": "1.2.0", "result": []}
        rich_fn = MagicMock()
        emit(data, output_json=False, output_xml=False, rich_fn=rich_fn, output_sarif=True)
        captured = capsys.readouterr()
        if '"version": "2.1.0"' not in captured.out:
            raise AssertionError
        rich_fn.assert_not_called()

    def test_emit_rich_calls_rich_fn(self):
        rich_fn = MagicMock()
        data = {"schema_version": "1.2.0", "result": {"key": "value"}}
        emit(data, output_json=False, output_xml=False, rich_fn=rich_fn, extra="kwarg")

        rich_fn.assert_called_once_with(data, extra="kwarg")

    def test_emit_rejects_non_dict_payload(self):
        data = ApiResponse.from_payload({"schema_version": "1.2.0", "result": {"key": "value"}})

        with pytest.raises(TypeError, match="dictionary payload"):
            emit(data, output_json=False, output_xml=False, rich_fn=MagicMock())
