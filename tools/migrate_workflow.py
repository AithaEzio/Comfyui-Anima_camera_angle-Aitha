"""Convert saved upstream UI / API JSON workflows without starting ComfyUI.

Run: python tools/migrate_workflow.py old.json [new-aitha.json]
The source is never overwritten. Linked legacy numeric inputs are rejected
because changing their names alone would silently change their units.
"""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from camera_core import DATA, number  # noqa: E402

CAMERA = "AithaCameraAngleNode"
EXTRAS = "AithaCameraExtraConfigNode"
AXES = {"pos_x": "horizontal_angle", "pos_y": "vertical_angle", "pos_z": "zoom"}
EXTREMES = {
    "\u65e0": "None", "\u6781\u9650\u4fef\u89c6": "Bird's-eye view [Tag]",
    "\u6781\u9650\u4ef0\u89c6": "Worm's-eye view [Description]",
}
OLD_EXTRA_FIELDS = (
    "extreme_type", "extreme_weight", "lens_enabled", "lens_value", "dof_enabled", "dof_value", "dof_weight",
    "movement_enabled", "movement_value", "composition_enabled", "composition_value", "style_enabled", "style_value",
)
OLD_EXTRA_DEFAULTS = ("\u65e0", 10, False, "85mm lens", False, "shallow depth of field", 1.3,
                      False, "handheld camera", False, "rule of thirds", False, "cinematic")


def camera_values(x, y, z):
    """Preserve the old viewport position, including its 15-degree offset."""
    return [
        (number(x, 0, -1, 1) * 180 + 360) % 360,
        number(y, 0, -1, 1) * 45 + 15,
        number(z, 0, -1, 1) * 4.5 + 5.5,
    ]


def extra_values(old):
    result = {
        "extreme_type": EXTREMES.get(old.get("extreme_type", "\u65e0")),
        "extreme_weight": number(old.get("extreme_weight", 10), 10, 0.1, 50),
    }
    if result["extreme_type"] is None:
        raise ValueError("Unknown legacy extreme viewpoint; choose one manually before converting.")
    for group in DATA["extra_groups"]:
        key = group["key"]
        result[f"{key}_preset"] = "Custom" if old.get(f"{key}_enabled") is True else "None"
        result[f"{key}_custom"] = old.get(f"{key}_value", "")
        result[f"{key}_weight"] = number(old.get("dof_weight", 1.3), 1.3, 0.1, 10) if key == "dof" else 1.0
    return result


def _legacy_array(node, defaults):
    raw = node.get("widgets_values", [])
    if not isinstance(raw, list):
        raise ValueError(f"Node {node.get('id')} has named widget values; only standard upstream arrays are supported.")
    return raw + list(defaults[len(raw):])


def _convert_ui(graph):
    count = 0
    string_sources = set()
    extra_targets = set()
    for node in graph.get("nodes", []):
        kind = node.get("type")
        if kind in ("CameraTagConfigNode", "CameraWeightConfigNode"):
            raise ValueError("This older workflow has separate tag / weight nodes. Merge those settings in the camera's settings panel before conversion.")
        if kind == "CameraAngleNode":
            for item in node.get("inputs", []):
                if item.get("name") in AXES and item.get("link") is not None:
                    raise ValueError(f"Camera node {node.get('id')} has a linked {item['name']}. Convert its upstream numeric range manually before replacing the node.")
            old = _legacy_array(node, (0, 0, 0, 0, "{}", ""))
            if len(old) > 5 and old[5]:
                raise ValueError("An inline extra_config value cannot become a forced input automatically. Connect it through a STRING node first.")
            node["widgets_values"] = [*camera_values(*old[:3]), old[3], old[4]]
            node["type"] = CAMERA
            string_sources.add(node["id"])
            node["title"] = "Anima Camera Angle - Aitha"
            node["size"] = [max(node.get("size", [400, 690])[0], 400), 690]
            for slot, item in enumerate(node.get("inputs", [])):
                item["name"] = AXES.get(item.get("name"), item.get("name"))
                if isinstance(item.get("widget"), dict):
                    item["widget"]["name"] = AXES.get(item["widget"].get("name"), item["widget"].get("name"))
                if item.get("name") == "extra_config":
                    item["type"] = "STRING"
                    extra_targets.add((node["id"], slot))
            for item in node.get("outputs", []):
                item["name"] = "camera_prompt"
                if "label" in item:
                    item["label"] = "camera_prompt"
            count += 1
        elif kind == "CameraExtraConfigNode":
            if any(item.get("link") is not None for item in node.get("inputs", [])):
                raise ValueError(f"Extra prompts node {node.get('id')} has connected legacy fields. Replace those connections manually before converting.")
            old = dict(zip(OLD_EXTRA_FIELDS, _legacy_array(node, OLD_EXTRA_DEFAULTS)))
            node["widgets_values"] = list(extra_values(old).values())
            node["type"] = EXTRAS
            string_sources.add(node["id"])
            node["title"] = "Anima Camera Extra Prompts - Aitha"
            node["size"] = [400, 450]
            outputs = node.setdefault("outputs", [])
            if not outputs:
                outputs.append({"name": "extra_config", "type": "STRING", "links": None})
            outputs[0]["name"] = "extra_config"
            if len(outputs) == 1:
                outputs.append({"name": "extra_prompt", "type": "STRING", "links": None})
            count += 1
        if node.get("type") in (CAMERA, EXTRAS):
            properties = node.setdefault("properties", {})
            properties["Node name for S&R"] = node["type"]
            # Upstream registry IDs would make Manager suggest the wrong package.
            for key in ("cnr_id", "aux_id", "ver"):
                properties.pop(key, None)
    for link in graph.get("links", []):
        if isinstance(link, list) and len(link) >= 6:
            if link[1] in string_sources or (link[3], link[4]) in extra_targets:
                link[5] = "STRING"
        elif isinstance(link, dict):
            if link.get("origin_id") in string_sources or (link.get("target_id"), link.get("target_slot")) in extra_targets:
                link["type"] = "STRING"
    for subgraph in graph.get("definitions", {}).get("subgraphs", []):
        count += _convert_ui(subgraph)
    return count


def _convert_api(prompt):
    count = 0
    for node in prompt.values():
        if not isinstance(node, dict):
            continue
        kind = node.get("class_type")
        inputs = node.get("inputs", {})
        if kind == "CameraAngleNode":
            if any(isinstance(inputs.get(key), (list, dict)) for key in AXES):
                raise ValueError("A legacy camera axis is connected to another node. Its numeric range must be converted manually.")
            converted = camera_values(*(inputs.get(key, 0) for key in AXES))
            for old, value in zip(AXES, converted):
                inputs.pop(old, None)
                inputs[AXES[old]] = value
            node["class_type"] = CAMERA
            count += 1
        elif kind == "CameraExtraConfigNode":
            if any(isinstance(value, (list, dict)) for value in inputs.values()):
                raise ValueError("Connected legacy extra prompt fields must be replaced manually before conversion.")
            node["inputs"] = extra_values({**dict(zip(OLD_EXTRA_FIELDS, OLD_EXTRA_DEFAULTS)), **inputs})
            node["class_type"] = EXTRAS
            count += 1
        elif kind in ("CameraTagConfigNode", "CameraWeightConfigNode"):
            raise ValueError("Separate legacy tag / weight nodes require manual conversion.")
    return count


def migrate_workflow(document):
    """Return a converted copy and node count. Leave all unrelated data intact."""
    result = deepcopy(document)
    if not isinstance(result, dict):
        raise ValueError("Expected a ComfyUI workflow or API prompt JSON object.")
    if isinstance(result.get("nodes"), list):
        count = _convert_ui(result)
    elif isinstance(result.get("prompt"), dict):
        count = _convert_api(result["prompt"])
    elif any(isinstance(value, dict) and "class_type" in value for value in result.values()):
        count = _convert_api(result)
    else:
        raise ValueError("No supported ComfyUI UI workflow or API prompt was found.")
    return result, count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--force", action="store_true", help="Replace an existing output file; never the input file.")
    args = parser.parse_args(argv)
    output = args.output or args.input.with_name(args.input.stem + "-aitha.json")
    try:
        if args.input.resolve() == output.resolve():
            raise ValueError("The output must be a different file from the source.")
        result, count = migrate_workflow(json.loads(args.input.read_text(encoding="utf-8-sig")))
        payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        with output.open("w" if args.force else "x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Conversion failed: {error}\n")
    print(f"Converted {count} node(s): {output}")
    if count:
        print("Review before use: positions preserve the old viewport. Corrected elevation / framing rules can change prompt text.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
