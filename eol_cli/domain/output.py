"""Pure output-selection policy for CLI rendering."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from eol_cli.domain.errors import OutputSelectionError


class OutputMode(Enum):
    """Allowed output format modes."""

    JSON = "json"
    XML = "xml"
    SARIF = "sarif"
    RICH = "rich"


@dataclass(frozen=True)
class OutputRenderResult:
    """Result of deciding how to render a command payload."""

    mode: OutputMode
    payload: object = ""
    rich_payload: object | None = None

    @property
    def is_rich(self) -> bool:
        """Return ``True`` when output should be rendered with Rich formatters."""
        return self.mode is OutputMode.RICH


def resolve_output_mode(output_json: bool, output_xml: bool, output_sarif: bool) -> OutputMode:
    """Resolve which output mode is requested and validate exclusivity."""
    if output_json and output_xml:
        raise OutputSelectionError("--json and --xml are mutually exclusive")
    if output_json and output_sarif:
        raise OutputSelectionError("--json and --sarif are mutually exclusive")
    if output_xml and output_sarif:
        raise OutputSelectionError("--xml and --sarif are mutually exclusive")

    if output_json:
        return OutputMode.JSON
    if output_xml:
        return OutputMode.XML
    if output_sarif:
        return OutputMode.SARIF
    return OutputMode.RICH


@dataclass(frozen=True)
class OutputFormatCommand:
    """Decision point for output serialization."""

    to_json: Callable[[dict[str, object]], str]
    to_xml: Callable[[dict[str, object]], str]
    to_sarif: Callable[[dict[str, object]], str]

    def resolve_mode(self, output_json: bool, output_xml: bool, output_sarif: bool) -> OutputMode:
        """Return the resolved output mode."""
        return resolve_output_mode(output_json, output_xml, output_sarif)

    def format_output(
        self, data: dict[str, object], output_json: bool, output_xml: bool, output_sarif: bool
    ) -> tuple[OutputMode, str]:
        """Format payload into the requested non-rich mode."""
        mode = self.resolve_mode(output_json, output_xml, output_sarif)
        if mode is OutputMode.JSON:
            return mode, self.to_json(data)
        if mode is OutputMode.XML:
            return mode, self.to_xml(data)
        if mode is OutputMode.SARIF:
            return mode, self.to_sarif(data)
        return mode, ""


@dataclass(frozen=True)
class RenderOutputCommand:
    """Build render plans for both rich and structured output modes."""

    output_format_command: OutputFormatCommand

    def run(
        self, data: dict[str, object], output_json: bool, output_xml: bool, output_sarif: bool
    ) -> OutputRenderResult:
        """Resolve output mode and prepare a render instruction."""
        mode, payload = self.output_format_command.format_output(
            data, output_json, output_xml, output_sarif
        )
        if mode is OutputMode.RICH:
            return OutputRenderResult(mode=mode, rich_payload=data)
        return OutputRenderResult(mode=mode, payload=payload, rich_payload=None)
