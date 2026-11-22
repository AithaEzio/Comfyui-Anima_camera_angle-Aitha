# Changelog

## 1.0.1 — Private settings socket fix

- Made the hidden tag-settings field socketless so it cannot overlap the real `extra_config` connector.
- Remove unused private settings sockets restored from earlier workflows after links have loaded, using LiteGraph's input-removal API to preserve the real connections and their slot indices.
- Added standalone regressions for fresh nodes, saved-workflow cleanup, preserved settings, and connected-input safety. ComfyUI was not run.

## 1.0.0 — Aitha fork

- Translated the node interface, viewport, help text, example, and documentation into English.
- Added Aitha-specific registration IDs and names, with an offline converter for existing upstream UI / API workflows.
- Replaced `pos_x`, `pos_y`, and `pos_z` with `horizontal_angle`, `vertical_angle`, and `zoom`, using Qwen-style units and synchronized preset dropdowns.
- Added all eight horizontal views, four elevations, and six framing presets while retaining continuous numeric control.
- Rebuilt Extra Prompts with 107 optional presets, four extreme viewpoints, custom text, per-group weights, and a standalone text output.
- Added an optional lighting group and source-linked preset reference / research notes.
- Fixed shared mutable defaults, zero-degree eye-level output, ignored zero extra-weight scale, mismatched preview behavior, and contradictory extreme / ordinary viewpoint tags.
- Added standalone backend, cross-language parity, frontend mock, and workflow conversion checks. ComfyUI / image-generation validation remains a manual release step.
- Removed tracked bytecode, unused unregistered configuration modules, and the dependency-heavy original example. Added a self-contained English controls example and release packaging utility.
