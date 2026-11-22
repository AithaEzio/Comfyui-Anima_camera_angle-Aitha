# Implementation decisions

## Fork identity and interface

The repository is named `Comfyui-Anima_camera_angle-Aitha`. Registration uses `AithaCameraAngleNode` and `AithaCameraExtraConfigNode`, without aliases for the upstream IDs. This permits coexistence. The English category is `Anima/Camera - Aitha`.

Camera values use Qwen-style names and ranges: azimuth 0–360°, elevation −30–60°, zoom 0–10. Roll retains the original 0–1 Dutch-angle switch semantics. Dropdowns add no serialized backend parameters; they set the same numeric widgets used by handles and API inputs.

The extra node keeps `extra_config` as its first STRING output and adds `extra_prompt` as the second. Its JSON schema version is 1, with optional `extreme` and an `extras` object containing the six groups. Each group contains `enabled`, `value`, and `weight`. The main node also accepts the old extras / extreme JSON keys. Malformed JSON and conflicting extreme viewpoints produce explicit errors.

## Shared data and prompt behavior

`js/camera_data.json` supplies all preset labels, values, research metadata, camera presets, and default tags. Python reads the local file; the frontend fetches it from the extension's own static directory. No runtime internet or external dependency download is needed.

`camera_core.py` and `js/camera_logic.js` implement matching pure calculations. Fresh nested settings prevent state from leaking between nodes. Standalone parity tests cover presets, weights, invalid data, and angle / framing behavior. The preview includes directly connected Aitha extras; external or dynamically linked values are marked partial until a server execution returns actual text.

The core retains the original continuous directional weighting and inherited angle multiplier of 10. It corrects eye-level output at zero degrees and uses actual signed elevation, without the original viewport's 15-degree bias. Medium framing uses `upper body`. Extreme viewpoints replace ordinary direction / elevation terms rather than adding contradictory terms.

## Frontend lifecycle

The extension uses the documented `nodeCreated` hook and standard `WEB_DIRECTORY` registration. Widget types stay intact while visibility changes, preserving custom text and hidden tag settings. Preview DOM widgets opt out of both workflow and API serialization. Local dropdown values and numeric readouts follow the same state as the scene.

The private `_tags_json` widget is declared hidden and socketless. Version 1.0.1 removes unused copies of its socket restored from older workflows in `loadedGraphNode`, after graph links exist. LiteGraph's `removeInput` API updates the remaining link slot indices; the tag widget and its saved value remain intact. Already-connected private sockets are preserved rather than silently disconnecting them.

The scene renders on changes and resize rather than continuously rebuilding geometry. Pointer capture keeps handle drags active outside the canvas. Wheel listeners are scoped to the owning canvas. Deletion clears polling, disconnects resize observers, aborts event listeners, and disposes GPU resources. If WebGL initialization fails, the dropdowns and numeric prompt controls remain usable.

API references reviewed: [ComfyUI frontend objects](https://docs.comfy.org/custom-nodes/js/javascript_objects_and_hijacking), [DOM widget implementation](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/scripts/domWidget.ts), and [widget visibility / serialization implementation](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/lib/litegraph/src/widgets/BaseWidget.ts). This source review is not a substitute for visual testing in ComfyUI.

## Migration and packaging

The converter returns a deep copy before writing a separate file. It renames only the upstream camera nodes, preserves graph IDs / connections and unrelated content, updates wildcard camera connections to STRING, and maps legacy widget values into degrees / zoom. Unsafe linked numeric conversions stop before output is written. Previously converted workflows are accepted without repeated rescaling.

The English example includes only the two Aitha nodes and a built-in note. The release ZIP uses an explicit source manifest with deterministic ordering / timestamps and includes licenses, documentation, tests, and conversion tools. Git metadata, old bytecode, and local caches are excluded. No GitHub publication or registry identity is configured automatically.
