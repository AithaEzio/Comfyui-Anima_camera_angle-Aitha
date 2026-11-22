"""Camera and preset logic, independent of ComfyUI and GPU dependencies.

Keep this module in parity with js/camera_logic.js. The shared catalog is the
single source for defaults, option labels, prompt text, and research sources.
"""

from copy import deepcopy
import json
import math
from pathlib import Path
import re

DATA = json.loads((Path(__file__).parent / "js" / "camera_data.json").read_text(encoding="utf-8"))
DEFAULT_TAGS = DATA["defaults"]
GROUP_KEYS = tuple(group["key"] for group in DATA["extra_groups"])


def number(value, default, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return default
    if isinstance(value, str) and not re.fullmatch(r"[+-]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:e[+-]?[0-9]+)?", value.strip(), re.IGNORECASE):
        return default
    try:
        result = float(value)
    except (ValueError, OverflowError):
        return default
    if not math.isfinite(result):
        return default
    if minimum is not None:
        result = max(minimum, result)
    if maximum is not None:
        result = min(maximum, result)
    return result


def _object(value, label):
    if value is None or value == "":
        return {}
    if isinstance(value, str):
        try:
            value = json.loads(value, parse_constant=_reject_constant)
        except (ValueError, TypeError) as error:
            raise ValueError(f"{label} must contain valid JSON.") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def _reject_constant(value):
    raise ValueError(f"Nonstandard JSON number: {value}")


def _overlay(default, override):
    """Merge known settings into fresh objects; never share mutable defaults."""
    if not isinstance(override, dict):
        return deepcopy(default)
    result = {}
    for key, value in default.items():
        candidate = override.get(key, value)
        if isinstance(value, dict):
            result[key] = _overlay(value, candidate)
        elif isinstance(value, bool):
            result[key] = candidate if isinstance(candidate, bool) else value
        elif isinstance(value, (int, float)):
            result[key] = number(candidate, value)
        else:
            result[key] = candidate if isinstance(candidate, str) else value
    return result


def settings(raw="{}"):
    result = _overlay(DEFAULT_TAGS, _object(raw, "Camera tag settings"))
    result["weight_max"] = number(result["weight_max"], 10, 0.1, 50)
    result["weight_min"] = number(result["weight_min"], 0.1, 0.1, result["weight_max"])
    result["extra_master"] = number(result["extra_master"], 1, 0, 20)
    result["xy_mult"] = number(result["xy_mult"], 10, 0.1, 50)
    result["azimuth"]["weight"] = number(result["azimuth"]["weight"], 10, 0.1, 50)
    result["azimuth"]["deadzone_ratio"] = number(result["azimuth"]["deadzone_ratio"], 0.05, 0, 1)
    for axis in ("azimuth", "elevation", "distance", "tilt"):
        result[axis]["extra"] = number(result[axis]["extra"], 0, -50, 50)
    return result


def normalize_camera(horizontal_angle=0, vertical_angle=0, zoom=4, roll=0):
    return {
        "horizontal_angle": number(horizontal_angle, 0, 0, 360) % 360,
        "vertical_angle": number(vertical_angle, 0, -30, 60),
        "zoom": number(zoom, 4, 0, 10),
        "roll": number(roll, 0, 0, 1),
    }


def distance_key(zoom):
    if zoom < 2:
        return "wide"
    if zoom < 2.75:
        return "full"
    if zoom < 3.5:
        return "cowboy_shot"
    if zoom < 6:
        return "medium"
    if zoom < 9:
        return "cu"
    return "ecu"


def _fmt_weight(weight):
    # Explicit half-up rounding also used by the JavaScript preview.
    return f"{math.floor(weight * 100 + 0.500000001) / 100:.2f}"


def _weighted_tags(value, weight):
    return [f"({tag.strip()}:{_fmt_weight(weight)})" for tag in value.split(",") if tag.strip()]


def _phrase(value, weight):
    value = value.strip()
    if not value:
        return ""
    return value if weight == 1 else f"({value}:{_fmt_weight(weight)})"


def _escape_tag(value):
    return value.replace("(", r"\(").replace(")", r"\)")


def build_extra_config(values):
    """Resolve labels to text; inactive custom text never enters the prompt."""
    extreme_label = values.get("extreme_type", "None")
    if not isinstance(extreme_label, str):
        raise ValueError("Extreme viewpoint preset must be a string.")
    extreme = next((p for p in DATA["extreme_presets"] if p["label"] == extreme_label), None)
    if extreme is None:
        raise ValueError(f"Unknown extreme viewpoint preset: {extreme_label}")
    result = {"schema_version": 1, "extras": {}}
    if extreme["value"]:
        result["extreme"] = {
            "tag": _escape_tag(extreme["value"]) if extreme["kind"] == "tag" else extreme["value"],
            "weight": number(values.get("extreme_weight", 1), 1, 0.1, 50),
        }
    for group in DATA["extra_groups"]:
        key = group["key"]
        selected = values.get(f"{key}_preset", "None")
        if not isinstance(selected, str):
            raise ValueError(f"{group['label']} preset must be a string.")
        value = ""
        if selected == "Custom":
            custom = values.get(f"{key}_custom", "")
            value = custom.strip() if isinstance(custom, str) else ""
        elif selected != "None":
            preset = next((p for p in group["presets"] if p["label"] == selected), None)
            if preset is None:
                raise ValueError(f"Unknown {group['label']} preset: {selected}")
            value = _escape_tag(preset["value"]) if preset["kind"] == "tag" else preset["value"]
        result["extras"][key] = {
            "enabled": bool(value), "value": value,
            "weight": number(values.get(f"{key}_weight", 1), 1, 0.1, 10),
        }
    return result


def normalize_extra_config(raw=""):
    config = _object(raw, "Extra configuration")
    if "schema_version" in config and (isinstance(config["schema_version"], bool) or config["schema_version"] != 1):
        raise ValueError("Unsupported extra configuration version; expected 1.")
    extras = _object(config.get("extras"), "Extra configuration extras")
    result = {"extras": {}}
    for key in GROUP_KEYS:
        entry = extras.get(key)
        if not isinstance(entry, dict):
            continue
        value = entry.get("value", "")
        if entry.get("enabled") is True and isinstance(value, str) and value.strip():
            result["extras"][key] = {
                "value": value.strip(), "enabled": True,
                "weight": number(entry.get("weight", 1.3 if key == "dof" else 1), 1, 0.1, 50),
            }
    # Old JSON configs remain readable, including the original DOF weight.
    extremes = [config[k] for k in ("extreme", "extreme_high", "extreme_low")
                if isinstance(config.get(k), dict) and isinstance(config[k].get("tag"), str)
                and config[k]["tag"].strip()]
    if len(extremes) > 1:
        raise ValueError("Choose one extreme viewpoint; the configuration contains conflicting viewpoints.")
    if extremes:
        result["extreme"] = {
            "tag": extremes[0]["tag"].strip(),
            "weight": number(extremes[0].get("weight", 1), 1, 0.1, 50),
        }
    return result


def extra_prompt(raw=""):
    config = normalize_extra_config(raw)
    parts = []
    if config.get("extreme"):
        extreme = config["extreme"]
        parts.append(_phrase(extreme["tag"], extreme["weight"]))
    for key in GROUP_KEYS:
        entry = config["extras"].get(key)
        if entry:
            parts.append(_phrase(entry["value"], entry["weight"]))
    return ", ".join(filter(None, parts))


def camera_prompt(horizontal_angle=0, vertical_angle=0, zoom=4, roll=0,
                  tags_json="{}", extra_config=""):
    camera = normalize_camera(horizontal_angle, vertical_angle, zoom, roll)
    config = settings(tags_json)
    extras = normalize_extra_config(extra_config)
    parts = []
    wmin, wmax, master = config["weight_min"], config["weight_max"], config["extra_master"]
    xy = config["xy_mult"] if config["xy_mult_enabled"] else None
    maximum = max(wmax, xy) if xy is not None else wmax
    azimuth = config["azimuth"]
    if azimuth["enabled"] and not extras.get("extreme"):
        angle = math.radians(camera["horizontal_angle"])
        ratios = {
            "front": max(0, math.cos(angle)), "back": max(0, -math.cos(angle)),
            "left": max(0, -math.sin(angle)), "right": max(0, math.sin(angle)),
        }
        total = sum(ratios.values())
        budget = (xy if xy is not None else azimuth["weight"]) + azimuth["extra"] * master
        cap = maximum + max(0, azimuth["extra"] * master)
        for direction, ratio in ratios.items():
            weight = ratio / total * budget
            if ratio > 1e-12 and weight >= azimuth["deadzone_ratio"]:
                parts.extend(_weighted_tags(azimuth["directions"][direction]["tag"], min(cap, max(wmin, weight))))
    elevation = config["elevation"]
    if elevation["enabled"] and not extras.get("extreme"):
        angle = camera["vertical_angle"]
        key = "low" if angle < -15 else "eye" if angle < 15 else "high"
        # Eye level must still emit a useful tag at precisely zero degrees.
        weight = max(1.0, abs(angle) / 90 * (xy if xy is not None else 10)) + master * elevation["extra"]
        if weight >= azimuth["deadzone_ratio"]:
            cap = maximum + max(0, elevation["extra"] * master)
            parts.extend(_weighted_tags(elevation["categories"][key]["tag"], min(cap, max(wmin, weight))))
    for axis, tag in (
        ("distance", config["distance"]["categories"][distance_key(camera["zoom"])]["tag"]),
        ("tilt", config["tilt"]["dutch_tag"] if camera["roll"] > 0 else ""),
    ):
        if config[axis]["enabled"] and tag:
            extra = config[axis]["extra"] * master
            parts.extend(_weighted_tags(tag, min(wmax + max(0, extra), max(0.1, 1 + extra))))
    text = extra_prompt(extras)
    if text:
        parts.append(text)
    return ", ".join(parts)
