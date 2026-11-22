"""Preset-driven additional camera and illustration prompts."""

import json

from .camera_core import DATA, build_extra_config, extra_prompt


class CameraExtraConfigNode:
    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "extreme_type": ([p["label"] for p in DATA["extreme_presets"]], {
                "default": "None",
                "tooltip": "Optional extreme viewpoint. Replaces the main node's horizontal and vertical tags to avoid contradictory angles.",
            }),
            "extreme_weight": ("FLOAT", {
                "default": 1.0, "min": 0.1, "max": 50.0, "step": 0.1,
                "tooltip": "Prompt emphasis for the extreme viewpoint. Start at 1 and adjust after inspecting an image.",
            }),
        }
        for group in DATA["extra_groups"]:
            key = group["key"]
            required[f"{key}_preset"] = (["None", "Custom", *[p["label"] for p in group["presets"]]], {
                "default": "None", "tooltip": group["tooltip"] + " Choose None to skip, or Custom for your own text.",
            })
            required[f"{key}_custom"] = ("STRING", {
                "default": "", "multiline": False,
                "tooltip": "Used only when this preset is Custom. Existing ComfyUI prompt weighting is preserved.",
            })
            required[f"{key}_weight"] = ("FLOAT", {
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1,
                "tooltip": "Emphasis for this group. 1 adds the text without an extra weight wrapper.",
            })
        return {"required": required}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("extra_config", "extra_prompt")
    FUNCTION = "execute"
    CATEGORY = "Anima/Camera - Aitha"
    DESCRIPTION = (
        "Choose optional presets for perspective, focus, motion effects, composition, style, and lighting. "
        "Connect extra_config to the camera node, or use extra_prompt as standalone text. "
        "Tag entries use booru vocabulary; Description entries use English captions. "
        "These are prompt suggestions, not measured lens settings or guaranteed image results."
    )

    def execute(self, extreme_type="None", extreme_weight=1.0, **kwargs):
        config = build_extra_config({"extreme_type": extreme_type, "extreme_weight": extreme_weight, **kwargs})
        prompt = extra_prompt(config)
        return {
            "ui": {"extra_prompt": [prompt]},
            "result": (json.dumps(config, ensure_ascii=False, allow_nan=False), prompt),
        }


NODE_CLASS_MAPPINGS = {"AithaCameraExtraConfigNode": CameraExtraConfigNode}
NODE_DISPLAY_NAME_MAPPINGS = {"AithaCameraExtraConfigNode": "Anima Camera Extra Prompts - Aitha"}
