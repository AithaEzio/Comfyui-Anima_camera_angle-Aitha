# Manual ComfyUI checks before release

These checks are intentionally left for the maintainer. They have **not** been run as part of the standalone validation.

## Installation and display

- Install alongside the original Anima camera extension and confirm both sets of nodes appear without registration conflicts.
- Load `examples/anima_camera_aitha.json`. Confirm English labels, an unclipped viewport, readable dropdowns, and no browser console errors.
- Resize both nodes at narrow and wide widths. Expand / collapse settings and switch every Extra Prompts group between None, a built-in preset, and Custom. Confirm custom fields, weights, and previews fit.
- Save and reload a workflow with edited tags, disabled axes, custom text, and nondefault weights. Confirm values and output stay the same.

## Camera and prompt controls

- Select all eight horizontal presets, all four elevations, and all six framing presets. Check dropdowns, numbers, handles, and prompt previews agree.
- Drag each handle, including beyond the canvas while pointer capture is active. Check release, cancellation, and wheel zoom. Wheel input outside the viewport should keep normal graph behavior.
- Reset the camera after editing tags. Confirm camera values reset while tag edits remain. Test the separate tag / weight reset.
- Connect Extra Prompts and compare the local preview with the executed `camera_prompt`. Check the separate `extra_prompt` output too.
- Choose each extreme viewpoint. Confirm ordinary horizontal / vertical tags are replaced, and framing remains in the prompt.
- Connect numeric inputs and an external JSON STRING source. Confirm linked controls are disabled where appropriate and execution displays the actual resulting prompt.
- Duplicate / delete several nodes and open / close workflows. Check rendering and event listeners remain responsive.

## Model generations

- Use a known working Anima workflow and fixed seed, sampler, resolution, and subject prompt. Compare one changed preset at a time against None.
- Check front / side / back views, positive / negative elevation, each framing category, focus isolation, motion cues, styles, and lighting.
- Start extra weights at 1. Tune the inherited camera angle multiplier for the checkpoint; test stronger values only as needed.
- Review Base, Aesthetic, or Turbo separately if claiming support for all of them. Avoid adding automatic quality / score tags to this helper during comparisons.
- Record the checkpoint, ComfyUI frontend version, prompt, seed, and observed limitations. Remove or relabel presets that consistently fail the intended visual effect.

## Workflow conversion

- Convert a copy of an upstream workflow. Confirm links and custom text survive and the original is unchanged.
- Inspect the 15-degree legacy elevation offset and the new framing categories; adjust the converted camera if needed.
- Confirm connected legacy numeric axes produce a conversion error, rather than an incorrectly rescaled connection.

Publish generation screenshots and frontend compatibility claims only after these manual checks are complete.
