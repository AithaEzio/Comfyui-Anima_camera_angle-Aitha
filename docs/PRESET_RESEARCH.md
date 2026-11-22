# Preset research and compatibility

Reviewed on **22 November 2026**. The supported prompting formats come from the model author; tag vocabulary and definitions come from the tag database documentation. This is an evidence-based selection of prompt suggestions, not a claim that each option has been image-tested.

## Primary evidence

| Source | What it establishes | Design consequence |
| --- | --- | --- |
| [CircleStone Labs: Anima model card](https://huggingface.co/circlestone-labs/Anima) | Training uses booru tags, English captions, and mixtures. Tag formatting uses lowercase and spaces. The model targets illustration; photorealism is outside its main strengths. | Offer tagged concepts and concrete English descriptions. Favor illustration vocabulary over camera-brand specifications. |
| [Danbooru: Image composition](https://safebooru.donmai.us/wiki_pages/tag_group:image_composition) | Documents viewpoint, perspective, body framing, composition, styles, and rendering techniques. | Use established terms for fisheye, foreshortening, framing, symmetry, line art, and other visual effects. |
| [Danbooru: From above](https://safebooru.donmai.us/wiki_pages/from_above) | Distinguishes an elevated viewpoint and the related bird's-eye concept. | Use `from above` for positive elevation; reserve the extreme selector for a stronger viewpoint description. |
| [Danbooru: Depth of field](https://safebooru.donmai.us/wiki_pages/depth_of_field) | The tag denotes selective blur, including foreground / background blur; links to bokeh and soft focus. | Do not equate deep focus with the blur tag. Provide a separate caption for a sharp foreground and background. |
| [Danbooru: Motion lines](https://safebooru.donmai.us/wiki_pages/motion_lines) | Defines motion lines and speed lines, with related motion blur and afterimages. | Replace ambiguous film-camera movement defaults with visible motion effects for still illustrations. |
| [Danbooru: Lighting](https://safebooru.donmai.us/wiki_pages/tag_group:lighting) | Documents light direction, light sources, shadows, and optical effects. | Add a dedicated optional lighting group, including useful direction and source choices. |
| [Danbooru: Traditional media](https://safebooru.donmai.us/wiki_pages/traditional_media) | Lists media vocabulary such as watercolor, gouache, graphite, and oil painting. | Offer illustration medium presets and escape literal parentheses for the ComfyUI prompt parser. |

Danbooru's `safebooru.donmai.us` host provides the same tag wiki with safe image filtering. Only text documentation was needed for this research.

## What “supported” means here

The model author's documentation establishes support for the **prompting formats and broad concepts**. It does not provide a complete whitelist or measured success rate for individual terms. Established tag vocabulary is a stronger basis than invented tags, but does not prove that every spelling was present in Anima's training captions or that every checkpoint will render it consistently.

Each built-in option is therefore labeled `[Tag]` or `[Description]`. Tag entries have source references in the shared catalog. Description entries are original English captions whose compatibility follows from Anima's documented caption prompting; their visual effectiveness remains an inference requiring generation tests.

When tag spellings differ between Gelbooru and Danbooru, the Anima author prefers Gelbooru's spelling. The selected tag entries use common vocabulary; the catalog does not claim a complete Gelbooru alias audit. Custom text remains available for checkpoint-specific vocabulary.

## Selection decisions

- **Lens / perspective:** prioritize visible distortion, perspective, foreshortening, and compression. Exact focal length, aperture, camera-brand, and sensor-size promises were excluded from built-in choices.
- **Focus:** offer both tagged blur effects and caption-based descriptions of where focus lies. These are stylistic instructions, not numeric optics controls.
- **Motion effects:** describe visible blur, line effects, wind, or a frozen action. Terms such as dolly, crane, orbit, and tracking shot were excluded because a still-image prompt cannot actually execute camera motion.
- **Composition:** include subject placement and framing. No automatic rewriting of the user's scene is attempted; conflicting choices remain the user's composition decision.
- **Style:** use illustration styles and art media. Artist-name lists, model-specific quality stacks, and photorealistic camera marketing phrases were excluded.
- **Lighting:** include direction, source, and atmospheric descriptions. Lighting presets alter prompt text; they do not alter viewport illumination.

No score or quality preset is inserted automatically. The author's Aesthetic guidance differs from Base guidance about score tags, so a camera helper should leave that checkpoint-specific decision to the user's main prompt.

## Traceability and maintenance

`js/camera_data.json` contains every label, exact output phrase, kind, source ID, and review date. Both runtimes read that same catalog. [PRESET_REFERENCE.md](PRESET_REFERENCE.md) renders its contents for review. Adding a preset requires an evidence / description classification and a matching standalone test run.

Review date describes the source check, not a claim of current or historical model-generation validation. No ComfyUI run, model download, GPU inference, or image comparison was performed for this work.
