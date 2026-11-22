"""ComfyUI interface for the Aitha camera prompt node."""

from .camera_core import camera_prompt


class CameraAngleNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "horizontal_angle": ("FLOAT", {
                    "default": 0.0, "min": 0.0, "max": 360.0, "step": 1.0,
                    "tooltip": "Camera azimuth in degrees: 0 front, 90 right, 180 back, 270 left.",
                }),
                "vertical_angle": ("FLOAT", {
                    "default": 0.0, "min": -30.0, "max": 60.0, "step": 1.0,
                    "tooltip": "Camera elevation in degrees. Negative looks up; positive looks down. 0 is eye level.",
                }),
                "zoom": ("FLOAT", {
                    "default": 4.0, "min": 0.0, "max": 10.0, "step": 0.1,
                    "tooltip": "Framing: 0 wide, 10 extreme close-up. This describes the prompt, not a physical lens.",
                }),
                "roll": ("FLOAT", {
                    "default": 0.0, "min": 0.0, "max": 1.0, "step": 0.1,
                    "tooltip": "0 disables Dutch angle; any positive value adds the tilt tag. Not an exact rotation in degrees.",
                }),
                "_tags_json": ("STRING", {
                    "default": "{}", "multiline": False, "hidden": True, "socketless": True,
                }),
            },
            "optional": {
                "extra_config": ("STRING", {
                    "forceInput": True,
                    "tooltip": "Connect extra_config from Anima Camera Extra Prompts - Aitha.",
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("camera_prompt",)
    FUNCTION = "execute"
    CATEGORY = "Anima/Camera - Aitha"
    DESCRIPTION = (
        "Build an English Anima camera prompt with synchronized sliders, preset dropdowns, "
        "and a 3D viewport. Edit tags and weights in the viewport's settings panel."
    )

    def execute(self, horizontal_angle, vertical_angle, zoom, roll=0.0,
                _tags_json="{}", extra_config=""):
        prompt = camera_prompt(horizontal_angle, vertical_angle, zoom, roll, _tags_json, extra_config)
        return {"ui": {"camera_prompt": [prompt]}, "result": (prompt,)}


NODE_CLASS_MAPPINGS = {"AithaCameraAngleNode": CameraAngleNode}
NODE_DISPLAY_NAME_MAPPINGS = {"AithaCameraAngleNode": "Anima Camera Angle - Aitha"}
