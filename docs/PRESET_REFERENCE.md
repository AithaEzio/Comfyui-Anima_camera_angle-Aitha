# Preset reference

Generated from `js/camera_data.json`. Run `python tools/export_preset_reference.py` after changing the catalog.

107 optional group presets and four extreme viewpoints. Every group also offers **None** and **Custom**. The output below uses weight 1; other weights add a prompt wrapper. Literal tag parentheses are escaped.

Tags are sourced vocabulary. Descriptions are English caption suggestions supported at the prompting-format level, with no claim of per-preset image validation. Append these extras to a subject / scene prompt. See [research and compatibility notes](PRESET_RESEARCH.md).

## Lens / perspective (15)

Illustrated perspective and lens effects. Lens descriptions are visual suggestions, not calibrated optics.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Fisheye distortion [Tag] | `fisheye` | [anima][anima], [composition][composition] |
| Strong perspective [Tag] | `perspective` | [anima][anima], [composition][composition] |
| Foreshortening [Tag] | `foreshortening` | [anima][anima], [composition][composition] |
| Atmospheric perspective [Tag] | `atmospheric perspective` | [anima][anima], [composition][composition] |
| Vanishing point [Tag] | `vanishing point` | [anima][anima], [composition][composition] |
| Panorama [Tag] | `panorama` | [anima][anima], [composition][composition] |
| Isometric perspective [Tag] | `isometric` | [anima][anima], [composition][composition] |
| Wide-angle look [Description] | `A wide-angle perspective shows the subject together with a broad view of the surroundings.` | [anima][anima] |
| Ultra-wide perspective [Description] | `An exaggerated wide-angle perspective makes nearby objects appear much larger than distant objects.` | [anima][anima] |
| Natural perspective [Description] | `The scene has natural proportions with little perspective distortion.` | [anima][anima] |
| Telephoto compression [Description] | `A compressed perspective makes the background appear close behind the subject.` | [anima][anima] |
| Orthographic look [Description] | `Parallel edges remain parallel and objects do not shrink noticeably with distance.` | [anima][anima] |
| Macro detail [Description] | `A tiny detail fills the frame and its fine surface texture is clearly visible.` | [anima][anima] |
| Enlarged foreground [Description] | `An object close to the viewer appears large while the subject and background recede behind it.` | [anima][anima] |
| Layered depth [Description] | `Near objects overlap the subject and distant scenery to create clear layers of depth.` | [anima][anima] |

## Focus / depth of field (12)

Choose what stays sharp and what becomes blurry. Deep focus is an English description, not a depth-of-field blur tag.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Depth of field [Tag] | `depth of field` | [anima][anima], [focus][focus] |
| Blurry background [Tag] | `blurry background` | [anima][anima], [focus][focus] |
| Blurry foreground [Tag] | `blurry foreground` | [anima][anima], [focus][focus] |
| Bokeh [Tag] | `bokeh` | [anima][anima], [focus][focus] |
| Soft focus [Tag] | `soft focus` | [anima][anima], [focus][focus] |
| Shallow focus [Description] | `The subject is sharply focused while the background falls softly out of focus.` | [anima][anima] |
| Deep focus [Description] | `The foreground and distant background are both sharply focused.` | [anima][anima] |
| Face in focus [Description] | `The face is sharply focused while the surroundings are softly blurred.` | [anima][anima] |
| Eyes in focus [Description] | `The eyes are the sharpest part of the image and the background is softly blurred.` | [anima][anima] |
| Hands in focus [Description] | `The hands and the object they hold are sharply focused while the background is blurred.` | [anima][anima] |
| Subject isolated by focus [Description] | `The subject is sharp between a softly blurred foreground and a softly blurred background.` | [anima][anima] |
| Distant haze [Description] | `The nearby subject is clear while distant scenery fades into a soft atmospheric haze.` | [anima][anima] |

## Motion effects (12)

Visible motion cues for a still image. These do not animate the camera or generate video.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Motion blur [Tag] | `motion blur` | [anima][anima], [motion][motion] |
| Motion lines [Tag] | `motion lines` | [anima][anima], [motion][motion] |
| Speed lines [Tag] | `speed lines` | [anima][anima], [motion][motion] |
| Afterimage [Tag] | `afterimage` | [anima][anima], [motion][motion] |
| Frozen action [Description] | `The subject is captured sharply in the middle of a fast action.` | [anima][anima] |
| Panning blur [Description] | `The moving subject remains sharp while the background streaks horizontally.` | [anima][anima] |
| Radial motion blur [Description] | `Blur streaks radiate outward from the subject to suggest rapid movement toward the viewer.` | [anima][anima] |
| Wind-swept motion [Description] | `Hair and loose clothing stream in the same direction in a strong wind.` | [anima][anima] |
| Falling motion [Description] | `The subject is suspended mid-fall with hair and loose fabric trailing upward.` | [anima][anima] |
| Gentle motion [Description] | `A small movement gently lifts loose hair and fabric.` | [anima][anima] |
| Dynamic action [Description] | `The subject is shown mid-action with a strong diagonal line of movement through the body.` | [anima][anima] |
| Still pose [Description] | `The subject and the surroundings are motionless with crisp edges.` | [anima][anima] |

## Composition (22)

Subject placement and framing. Choose a preset that agrees with the camera framing and viewpoint.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Negative space [Tag] | `negative space` | [anima][anima], [composition][composition] |
| Symmetry [Tag] | `symmetry` | [anima][anima], [composition][composition] |
| Letterboxed [Tag] | `letterboxed` | [anima][anima], [composition][composition] |
| First-person viewpoint [Tag] | `pov` | [anima][anima], [composition][composition] |
| Portrait framing [Tag] | `portrait` | [anima][anima], [composition][composition] |
| Upper-body framing [Tag] | `upper body` | [anima][anima], [composition][composition] |
| Full-body framing [Tag] | `full body` | [anima][anima], [composition][composition] |
| Landscape [Tag] | `landscape` | [anima][anima], [composition][composition] |
| Scenery [Tag] | `scenery` | [anima][anima], [composition][composition] |
| Silhouette [Tag] | `silhouette` | [anima][anima], [composition][composition] |
| Centered subject [Description] | `The subject is centered in the frame.` | [anima][anima] |
| Rule of thirds [Description] | `The subject is placed near a rule-of-thirds intersection with open space on the opposite side.` | [anima][anima] |
| Leading lines [Description] | `Lines in the environment lead the eye toward the subject.` | [anima][anima] |
| Frame within a frame [Description] | `An archway or doorway surrounds the subject and forms a frame inside the image.` | [anima][anima] |
| Foreground / middle / background [Description] | `The image has a distinct foreground, a subject in the middle distance, and a distant background.` | [anima][anima] |
| Diagonal composition [Description] | `The main shapes run diagonally across the frame.` | [anima][anima] |
| Subject on the left [Description] | `The subject occupies the left third of the image with open space on the right.` | [anima][anima] |
| Subject on the right [Description] | `The subject occupies the right third of the image with open space on the left.` | [anima][anima] |
| Over-the-shoulder [Description] | `The scene is viewed over a foreground character's shoulder toward the main subject.` | [anima][anima] |
| Small subject / large setting [Description] | `The subject appears small within a large, detailed environment.` | [anima][anima] |
| Triangular arrangement [Description] | `The main visible elements form a clear triangular arrangement.` | [anima][anima] |
| Room to look into [Description] | `Open space extends in front of the direction the subject is facing.` | [anima][anima] |

## Illustration style (24)

Art styles and media found in illustration tagging. No artist names or automatic quality / score tags are added.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Anime screenshot [Tag] | `anime screenshot` | [anima][anima], [composition][composition] |
| Official art [Tag] | `official art` | [anima][anima], [composition][composition] |
| Line art [Tag] | `lineart` | [anima][anima], [composition][composition] |
| Sketch [Tag] | `sketch` | [anima][anima], [composition][composition] |
| Painterly [Tag] | `painterly` | [anima][anima], [composition][composition] |
| Pixel art [Tag] | `pixel art` | [anima][anima], [composition][composition] |
| Ink wash painting [Tag] | `ink wash painting` | [anima][anima], [composition][composition] |
| Watercolor [Tag] | `watercolor \(medium\)` | [anima][anima], [media][media] |
| Oil painting [Tag] | `oil painting \(medium\)` | [anima][anima], [media][media] |
| Gouache [Tag] | `gouache \(medium\)` | [anima][anima], [media][media] |
| Colored pencil [Tag] | `colored pencil \(medium\)` | [anima][anima], [media][media] |
| Charcoal [Tag] | `charcoal \(medium\)` | [anima][anima], [media][media] |
| Graphite [Tag] | `graphite \(medium\)` | [anima][anima], [media][media] |
| Halftone [Tag] | `halftone` | [anima][anima], [composition][composition] |
| Crosshatching [Tag] | `crosshatching` | [anima][anima], [composition][composition] |
| Pointillism [Tag] | `pointillism` | [anima][anima], [composition][composition] |
| Art Nouveau [Tag] | `art nouveau` | [anima][anima], [composition][composition] |
| Art Deco [Tag] | `art deco` | [anima][anima], [composition][composition] |
| Ukiyo-e [Tag] | `ukiyo-e` | [anima][anima], [composition][composition] |
| Impressionism [Tag] | `impressionism` | [anima][anima], [composition][composition] |
| Minimalism [Tag] | `minimalism` | [anima][anima], [composition][composition] |
| Abstract [Tag] | `abstract` | [anima][anima], [composition][composition] |
| Surreal [Tag] | `surreal` | [anima][anima], [composition][composition] |
| Flat-color anime [Description] | `The illustration uses clean outlines, flat color areas, and simple cel shading.` | [anima][anima] |

## Lighting (22)

Optional lighting direction, source, and atmosphere. Lighting affects appearance; it does not change the 3D viewport lights.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Backlighting [Tag] | `backlighting` | [anima][anima], [lighting][lighting] |
| Light from above [Tag] | `overlighting` | [anima][anima], [lighting][lighting] |
| Side lighting [Tag] | `sidelighting` | [anima][anima], [lighting][lighting] |
| Light from below [Tag] | `underlighting` | [anima][anima], [lighting][lighting] |
| Sunlight [Tag] | `sunlight` | [anima][anima], [lighting][lighting] |
| Moonlight [Tag] | `moonlight` | [anima][anima], [lighting][lighting] |
| Dappled sunlight [Tag] | `dappled sunlight` | [anima][anima], [lighting][lighting] |
| Light rays [Tag] | `light rays` | [anima][anima], [lighting][lighting] |
| Dim lighting [Tag] | `dim lighting` | [anima][anima], [lighting][lighting] |
| Spotlight [Tag] | `spotlight` | [anima][anima], [lighting][lighting] |
| Bloom [Tag] | `bloom` | [anima][anima], [lighting][lighting] |
| Chiaroscuro [Tag] | `chiaroscuro` | [anima][anima], [lighting][lighting] |
| Candlelight [Tag] | `candlelight` | [anima][anima], [lighting][lighting] |
| Caustics [Tag] | `caustics` | [anima][anima], [lighting][lighting] |
| Rim light [Description] | `A narrow rim of light traces the outer edge of the subject.` | [anima][anima] |
| Soft window light [Description] | `Soft daylight enters through a nearby window and gently lights one side of the subject.` | [anima][anima] |
| Golden-hour light [Description] | `Low, warm sunlight creates long shadows and a golden glow.` | [anima][anima] |
| Overcast daylight [Description] | `An overcast sky creates soft, even illumination with faint shadows.` | [anima][anima] |
| Neon light [Description] | `Colored neon lights cast vivid pink and blue light across the subject.` | [anima][anima] |
| Soft diffuse light [Description] | `Broad, diffuse light illuminates the subject with soft shadows.` | [anima][anima] |
| Warm / cool split light [Description] | `Warm light illuminates one side of the subject while cool light illuminates the other.` | [anima][anima] |
| Bright background silhouette [Description] | `The subject appears as a dark silhouette against a bright background.` | [anima][anima] |

## Extreme viewpoints (4)

These replace the camera node's ordinary horizontal and vertical prompt tags.

| Preset | Output at weight 1 | Sources |
| --- | --- | --- |
| Bird's-eye view [Tag] | `bird's eye view` | [anima][anima], [above][above] |
| Worm's-eye view [Description] | `The camera is near the ground and looks steeply upward at the subject.` | [anima][anima] |
| Directly overhead [Description] | `The camera looks straight down at the subject from directly overhead.` | [anima][anima] |
| Directly underneath [Description] | `The camera looks straight up at the subject from directly underneath.` | [anima][anima] |

[anima]: https://huggingface.co/circlestone-labs/Anima
[composition]: https://safebooru.donmai.us/wiki_pages/tag_group:image_composition
[lighting]: https://safebooru.donmai.us/wiki_pages/tag_group:lighting
[focus]: https://safebooru.donmai.us/wiki_pages/depth_of_field
[motion]: https://safebooru.donmai.us/wiki_pages/motion_lines
[media]: https://safebooru.donmai.us/wiki_pages/traditional_media
[above]: https://safebooru.donmai.us/wiki_pages/from_above
