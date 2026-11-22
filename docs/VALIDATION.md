# Validation record

Checked on **22 November 2026** using Python 3.14.6 and Node.js 26.8.2 on Windows. These are standalone code checks, without a ComfyUI process, model download, or image generation.

| Check | Result |
| --- | --- |
| Python unit suite | **20 passed**. Covers English schema / IDs, defaults, angle and framing boundaries, mutable-state isolation, disabled axes, custom / built-in extras, literal tag parentheses, extreme overrides, invalid data, example consistency, and migration. |
| Python / JavaScript parity | **585 comparison cases passed**, within the Python suite. Covers randomized weights / angles, all 107 group presets, extreme viewpoints, malformed configs, explicit zeroes, and numeric / type edge cases. |
| Frontend mock suite | **9 passed**. Loads the real extension against small app / DOM stubs, with WebGL intentionally unavailable. Covers dropdown synchronization, dynamic field visibility, workflow restoration, custom text preservation, connected extras, actual execution previews, asynchronous copying, timer cleanup, nonserialized preview widgets, socketless internal settings, and cleanup of stale sockets without losing real connections. |
| JavaScript syntax | `npm run check` passed for both authored frontend modules. |
| Python compatibility syntax | All eight authored Python files parsed with Python 3.10 syntax rules. This is a syntax check, not a Python 3.10 runtime execution. |
| Upstream workflow conversion | The actual example from upstream commit `a89bbcd1ea02e79c08e5dd6e00f41961991d8ada` converted both camera nodes while preserving all **24** connection IDs and endpoints. |
| Catalog reference | Generated preset reference matches the shared runtime catalog. Every built-in option has an evidence classification and source IDs. |
| Translation / whitespace | Authored source and docs checked for remaining CJK text; none found. Legacy Chinese values exist only as Unicode escapes inside conversion mappings. `git diff --check` passed. |

The maintainer supplied a ComfyUI screenshot showing both connected nodes and the rendered 3D guide. That screenshot is included in the README; it does not establish a complete frontend or model-generation test matrix.

## Limits

The mock suite is not a browser layout or WebGL rendering test. It cannot establish frontend-version compatibility, pointer / wheel behavior in a real graph canvas, saved-workflow behavior in every ComfyUI frontend, or image adherence to camera / style presets.

The research supports the prompting formats and selected vocabulary; it is not per-preset generation validation. Before public release, use [MANUAL_COMFYUI_CHECKS.md](MANUAL_COMFYUI_CHECKS.md) and record the frontend / checkpoint versions actually tested.

The standalone checks do not publish a repository or establish registry compatibility. Upstream Git history and author attribution are retained.
