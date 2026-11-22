"""Regenerate the readable preset reference from the shared runtime catalog."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from camera_core import DATA, build_extra_config, extra_prompt  # noqa: E402


def render_reference():
    lines = [
        "# Preset reference", "",
        "Generated from `js/camera_data.json`. Run `python tools/export_preset_reference.py` after changing the catalog.", "",
        "107 optional group presets and four extreme viewpoints. Every group also offers **None** and **Custom**. "
        "The output below uses weight 1; other weights add a prompt wrapper. Literal tag parentheses are escaped.", "",
        "Tags are sourced vocabulary. Descriptions are English caption suggestions supported at the prompting-format level, "
        "with no claim of per-preset image validation. Append these extras to a subject / scene prompt. "
        "See [research and compatibility notes](PRESET_RESEARCH.md).", "",
    ]
    for group in DATA["extra_groups"]:
        lines.extend([f"## {group['label']} ({len(group['presets'])})", "", group["tooltip"], "",
                      "| Preset | Output at weight 1 | Sources |", "| --- | --- | --- |"])
        for preset in group["presets"]:
            output = extra_prompt(build_extra_config({f"{group['key']}_preset": preset["label"]}))
            sources = ", ".join(f"[{source}][{source}]" for source in preset["sources"])
            output = output.replace("|", r"\|")
            lines.append(f"| {preset['label']} | `{output}` | {sources} |")
        lines.append("")
    lines.extend(["## Extreme viewpoints (4)", "", "These replace the camera node's ordinary horizontal and vertical prompt tags.", "",
                  "| Preset | Output at weight 1 | Sources |", "| --- | --- | --- |"])
    for preset in DATA["extreme_presets"][1:]:
        output = extra_prompt(build_extra_config({"extreme_type": preset["label"]}))
        sources = ", ".join(f"[{source}][{source}]" for source in preset["sources"])
        lines.append(f"| {preset['label']} | `{output}` | {sources} |")
    lines.append("")
    for source, reference in DATA["sources"].items():
        lines.append(f"[{source}]: {reference['url']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    output = ROOT / "docs" / "PRESET_REFERENCE.md"
    output.write_text(render_reference(), encoding="utf-8")
    print(output)
