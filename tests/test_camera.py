"""Standalone validation. These tests never import or launch ComfyUI."""

from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import camera_core as core
from tools.migrate_workflow import migrate_workflow, camera_values, main as migrate_main
from tools.export_preset_reference import render_reference

spec = importlib.util.spec_from_file_location("aitha_test_package", ROOT / "__init__.py", submodule_search_locations=[str(ROOT)])
package = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = package
spec.loader.exec_module(package)
Camera = package.NODE_CLASS_MAPPINGS["AithaCameraAngleNode"]
Extras = package.NODE_CLASS_MAPPINGS["AithaCameraExtraConfigNode"]


class CameraTests(unittest.TestCase):
    def test_schema_and_isolated_registration(self):
        self.assertEqual(set(package.NODE_CLASS_MAPPINGS), {"AithaCameraAngleNode", "AithaCameraExtraConfigNode"})
        self.assertEqual(package.WEB_DIRECTORY, "./js")
        self.assertEqual(list(Camera.INPUT_TYPES()["required"]), ["horizontal_angle", "vertical_angle", "zoom", "roll", "_tags_json"])
        self.assertEqual(Camera.INPUT_TYPES()["optional"]["extra_config"][0], "STRING")
        private_settings = Camera.INPUT_TYPES()["required"]["_tags_json"][1]
        self.assertIs(private_settings["socketless"], True)
        self.assertIs(private_settings["hidden"], True)
        self.assertTrue(Camera.INPUT_TYPES()["optional"]["extra_config"][1]["forceInput"])
        self.assertNotIn("nodes", sys.modules)

    def test_defaults_and_angle_meanings(self):
        prompt = core.camera_prompt()
        self.assertEqual(prompt, "(straight-on:10.00), (eye-level view:1.00), (upper body:1.00)")
        self.assertEqual(prompt, core.camera_prompt(360))
        self.assertIn("from above", core.camera_prompt(0, 30))
        self.assertIn("from below", core.camera_prompt(0, -30))
        self.assertIn("facing left", core.camera_prompt(90))
        self.assertIn("facing right", core.camera_prompt(270))
        self.assertNotIn("straight-on", core.camera_prompt(90, tags_json={"azimuth": {"deadzone_ratio": 0}}))
        self.assertIn("from behind", core.camera_prompt(180))
        self.assertIn("dutch angle", core.camera_prompt(roll=0.1))

    def test_all_zoom_boundaries(self):
        for value, expected in [(0, "wide"), (1.999, "wide"), (2, "full"), (2.749, "full"),
                                (2.75, "cowboy_shot"), (3.499, "cowboy_shot"), (3.5, "medium"),
                                (5.999, "medium"), (6, "cu"), (8.999, "cu"), (9, "ecu"), (10, "ecu")]:
            with self.subTest(value=value):
                self.assertEqual(core.distance_key(value), expected)

    def test_settings_do_not_leak_across_nodes_or_calls(self):
        original = deepcopy(core.DEFAULT_TAGS)
        override = {"azimuth": {"directions": {"front": {"tag": "custom front"}}}, "elevation": {"enabled": False}}
        modified = core.camera_prompt(tags_json=override)
        self.assertIn("custom front", modified)
        self.assertNotIn("eye-level", modified)
        self.assertIn("straight-on", core.camera_prompt())
        first, second = core.settings(), core.settings()
        first["distance"]["enabled"] = False
        self.assertTrue(second["distance"]["enabled"])
        self.assertEqual(core.DEFAULT_TAGS, original)

    def test_zero_master_and_axis_switches(self):
        config = {"extra_master": 0, "azimuth": {"extra": 10}}
        self.assertEqual(core.camera_prompt(tags_json=config), core.camera_prompt())
        disabled = {key: {"enabled": False} for key in ("azimuth", "elevation", "distance", "tilt")}
        self.assertEqual(core.camera_prompt(roll=1, tags_json=disabled), "")

    def test_bad_numbers_and_partial_settings(self):
        self.assertEqual(core.camera_prompt(float("nan"), float("inf"), float("nan")), core.camera_prompt())
        self.assertEqual(core.normalize_camera(999, -999, 999, -1), {"horizontal_angle": 0.0, "vertical_angle": -30, "zoom": 10, "roll": 0})
        self.assertEqual(core.settings({"azimuth": None})["azimuth"], core.DEFAULT_TAGS["azimuth"])
        self.assertEqual(core.settings({"xy_mult": "nan"})["xy_mult"], 10)
        self.assertEqual(core.settings({"xy_mult": "0x20"})["xy_mult"], 10)
        self.assertEqual(core.settings({"xy_mult": "1_0"})["xy_mult"], 10)
        for value in ("{", "[]", "null", 3):
            with self.subTest(value=value), self.assertRaises(ValueError):
                core.camera_prompt(tags_json=value)

    def test_friendly_defaults_and_all_presets(self):
        self.assertEqual(core.extra_prompt(core.build_extra_config({})), "")
        count = 0
        for group in core.DATA["extra_groups"]:
            labels = [p["label"] for p in group["presets"]]
            self.assertEqual(len(labels), len(set(labels)))
            self.assertGreaterEqual(len(labels), 12)
            for preset in group["presets"]:
                with self.subTest(group=group["key"], preset=preset["label"]):
                    config = core.build_extra_config({f"{group['key']}_preset": preset["label"]})
                    text = core.extra_prompt(config)
                    self.assertTrue(text)
                    self.assertIn(text, core.camera_prompt(extra_config=config))
                    self.assertTrue(all(source in core.DATA["sources"] for source in preset["sources"]))
                    if preset["kind"] == "tag":
                        self.assertEqual(preset["value"], preset["value"].lower())
                        self.assertNotIn("_", preset["value"])
                    count += 1
        self.assertEqual(count, 107)

    def test_custom_text_and_literal_tag_parentheses(self):
        values = {"lens_preset": "Custom", "lens_custom": "  85mm lens, (soft light:1.2)  ", "lens_weight": 1.5,
                  "style_preset": "Watercolor [Tag]", "style_custom": "THIS MUST NOT APPEAR"}
        text = core.extra_prompt(core.build_extra_config(values))
        self.assertIn("(85mm lens, (soft light:1.2):1.50)", text)
        self.assertIn(r"watercolor \(medium\)", text)
        self.assertNotIn("MUST NOT", text)
        self.assertEqual(core.extra_prompt(core.build_extra_config({"lens_custom": "ignored"})), "")

    def test_extreme_angles_replace_other_angle_tags(self):
        for preset in core.DATA["extreme_presets"][1:]:
            config = core.build_extra_config({"extreme_type": preset["label"]})
            prompt = core.camera_prompt(90, 30, 4, 0, extra_config=config)
            self.assertIn(preset["value"], prompt)
            for conflicting in ("facing left", "from side", "from above", "eye-level"):
                self.assertNotIn(conflicting, prompt)
            self.assertIn("upper body", prompt)
        self.assertEqual(core.build_extra_config({"extreme_type": core.DATA["extreme_presets"][1]["label"], "extreme_weight": 50})["extreme"]["weight"], 50)

    def test_legacy_extra_json_and_explicit_errors(self):
        config = {"extras": {"dof": {"enabled": True, "value": "shallow depth of field"}},
                  "extreme_high": {"tag": "extreme high-angle shot", "weight": 4}}
        self.assertIn("(shallow depth of field:1.30)", core.extra_prompt(json.dumps(config)))
        self.assertIn("(extreme high-angle shot:4.00)", core.extra_prompt(config))
        for bad in ("{", "[]", {"schema_version": 2}, {"extras": []},
                    {"extreme_high": {"tag": "high"}, "extreme_low": {"tag": "low"}}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                core.normalize_extra_config(bad)
        with self.assertRaisesRegex(ValueError, "Unknown Lens"):
            core.build_extra_config({"lens_preset": "invented"})

    def test_node_outputs_and_preview_messages(self):
        extra = Extras().execute(style_preset="Sketch [Tag]", style_weight=1.5)
        config, text = extra["result"]
        self.assertEqual(text, extra["ui"]["extra_prompt"][0])
        output = Camera().execute(0, 0, 4, extra_config=config)
        self.assertIn(text, output["result"][0])
        self.assertEqual(output["result"][0], output["ui"]["camera_prompt"][0])

    def test_example_and_generated_reference_match_runtime(self):
        example = json.loads((ROOT / "examples" / "anima_camera_aitha.json").read_text(encoding="utf-8"))
        nodes = {node["id"]: node for node in example["nodes"]}
        for node in example["nodes"]:
            if node["type"] in package.NODE_CLASS_MAPPINGS:
                schema = package.NODE_CLASS_MAPPINGS[node["type"]].INPUT_TYPES()["required"]
                self.assertEqual(len(node["widgets_values"]), len(schema))
                for value, (kind, options) in zip(node["widgets_values"], schema.values()):
                    if isinstance(kind, list):
                        self.assertIn(value, kind)
        for link, source, output, target, input_slot, kind in example["links"]:
            self.assertIn(link, nodes[source]["outputs"][output]["links"])
            self.assertEqual(nodes[target]["inputs"][input_slot]["link"], link)
            self.assertEqual(kind, nodes[source]["outputs"][output]["type"])
        self.assertEqual((ROOT / "docs" / "PRESET_REFERENCE.md").read_text(encoding="utf-8"), render_reference())


class MigrationTests(unittest.TestCase):
    def workflow(self):
        return {"nodes": [
            {"id": 1, "type": "CameraExtraConfigNode", "widgets_values": ["\u6781\u9650\u4fef\u89c6", 10, True, "85mm lens", False, "shallow depth of field", 1.3, False, "handheld camera", False, "rule of thirds", False, "cinematic"],
             "inputs": [], "outputs": [{"name": "extra_config", "type": "STRING", "links": [10]}]},
            {"id": 2, "type": "CameraAngleNode", "widgets_values": [-0.5, 0, 0, 0, '{"azimuth":{"extra":2}}', ""],
             "inputs": [{"name": "extra_config", "type": "*", "link": 10}], "outputs": [{"name": "old", "type": "STRING", "links": [11]}]},
            {"id": 3, "type": "UnrelatedNode", "widgets_values": ["keep this text"], "inputs": [{"name": "text", "type": "STRING", "link": 11}]},
        ], "links": [[10, 1, 0, 2, 0, "STRING"], [11, 2, 0, 3, 0, "STRING"]], "groups": [{"title": "User group"}]}

    def test_ui_preserves_links_custom_text_and_source(self):
        source = self.workflow()
        before = deepcopy(source)
        result, count = migrate_workflow(source)
        self.assertEqual(source, before)
        self.assertEqual(count, 2)
        self.assertEqual(result["links"], source["links"])
        self.assertEqual(result["nodes"][2], source["nodes"][2])
        self.assertEqual(result["nodes"][1]["widgets_values"][:3], [270, 15, 5.5])
        self.assertEqual(result["nodes"][0]["widgets_values"][2:5], ["Custom", "85mm lens", 1.0])
        self.assertEqual(result["nodes"][1]["widgets_values"][4], source["nodes"][1]["widgets_values"][4])
        self.assertEqual(migrate_workflow(result), (result, 0))

    def test_axis_endpoint_mapping(self):
        self.assertEqual(camera_values(-1, -1, -1), [180, -30, 1])
        self.assertEqual(camera_values(1, 1, 1), [180, 60, 10])

    def test_legacy_wildcard_links_get_correct_string_type(self):
        source = self.workflow()
        source["links"][0][5] = "*"
        result, _ = migrate_workflow(source)
        self.assertEqual(result["links"][0][5], "STRING")
        self.assertEqual(result["links"][0][:5], source["links"][0][:5])

    def test_api_plain_and_wrapped(self):
        source = {"1": {"class_type": "CameraAngleNode", "inputs": {"pos_x": 0.5, "pos_y": -1, "pos_z": 1, "roll": 0, "extra_config": ["2", 0]}},
                  "2": {"class_type": "CameraExtraConfigNode", "inputs": {"style_enabled": True, "style_value": "custom style"}}}
        result, count = migrate_workflow(source)
        self.assertEqual(count, 2)
        self.assertEqual(result["1"]["inputs"]["horizontal_angle"], 90)
        self.assertEqual(result["1"]["inputs"]["extra_config"], ["2", 0])
        self.assertEqual(result["2"]["inputs"]["style_custom"], "custom style")
        wrapped, count = migrate_workflow({"prompt": source, "client_id": "keep"})
        self.assertEqual(wrapped["prompt"], result)
        self.assertEqual(wrapped["client_id"], "keep")

    def test_unsafe_connected_ranges_fail_before_output(self):
        source = self.workflow()
        source["nodes"][1]["inputs"].append({"name": "pos_x", "link": 30})
        with self.assertRaisesRegex(ValueError, "linked pos_x"):
            migrate_workflow(source)
        with self.assertRaises(ValueError):
            migrate_workflow({"1": {"class_type": "CameraAngleNode", "inputs": {"pos_x": ["9", 0]}}})

    def test_nested_subgraph(self):
        source = {"nodes": [], "definitions": {"subgraphs": [self.workflow()]}}
        result, count = migrate_workflow(source)
        self.assertEqual(count, 2)
        self.assertEqual(result["definitions"]["subgraphs"][0]["nodes"][1]["type"], "AithaCameraAngleNode")

    def test_cli_preserves_source_and_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "old.json"
            original = json.dumps(self.workflow())
            path.write_text(original, encoding="utf-8")
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                self.assertEqual(migrate_main([str(path)]), 0)
            output = path.with_name("old-aitha.json")
            self.assertTrue(output.exists())
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
                migrate_main([str(path)])
            with self.assertRaises(SystemExit), redirect_stderr(StringIO()):
                migrate_main([str(path), str(path), "--force"])


class FrontendParityTests(unittest.TestCase):
    def test_python_and_javascript_agree(self):
        rng = random.Random(62175)
        cases = []
        for i in range(350):
            tags = {
                "xy_mult_enabled": rng.choice([False, True]), "xy_mult": rng.uniform(0.1, 30),
                "extra_master": rng.choice([0, 1, 2]),
                "azimuth": {"extra": rng.uniform(-10, 10), "enabled": i % 7 != 0},
                "elevation": {"extra": rng.uniform(-10, 10)},
                "distance": {"extra": rng.uniform(-10, 10), "enabled": i % 11 != 0},
            }
            cases.append({"method": "cameraPrompt", "args": [rng.uniform(-20, 380), rng.uniform(-60, 90), rng.uniform(-1, 11), rng.random(), tags]})
        for group in core.DATA["extra_groups"]:
            for preset in group["presets"]:
                values = {f"{group['key']}_preset": preset["label"], f"{group['key']}_weight": rng.choice([1, 1.3, 2])}
                cases.extend([{"method": "buildExtraConfig", "args": [values]}, {"method": "extraPrompt", "args": [core.build_extra_config(values)]}])
        for extreme in core.DATA["extreme_presets"]:
            config = core.build_extra_config({"extreme_type": extreme["label"]})
            cases.append({"method": "cameraPrompt", "args": [45, 30, 4, 0, "{}", config]})
        for raw in ("{", "[]", "NaN", {"schema_version": 2}, {"schema_version": True}, {"extras": []}, {"extras": {"dof": {"enabled": True, "value": "focus"}}}, {"extras": {"dof": {"enabled": True, "value": "focus", "weight": None}}}):
            cases.append({"method": "normalizeExtraConfig", "args": [raw]})
        for raw in ({"extra_master": 0}, {"azimuth": None}, {"elevation": {"categories": {"high": None}}}, {"xy_mult": "nan"}, {"xy_mult": "0x20"}, {"xy_mult": "1_0"}):
            cases.append({"method": "settings", "args": [raw]})
        for raw in ({"lens_preset": None}, {"extreme_type": False}):
            cases.append({"method": "buildExtraConfig", "args": [raw]})
        functions = {"cameraPrompt": core.camera_prompt, "extraPrompt": core.extra_prompt,
                     "buildExtraConfig": core.build_extra_config, "normalizeExtraConfig": core.normalize_extra_config,
                     "settings": core.settings}
        result = subprocess.run(["node", str(ROOT / "tests" / "parity_runner.mjs")], input=json.dumps(cases), text=True,
                                encoding="utf-8", capture_output=True, check=True, cwd=ROOT)
        actual = json.loads(result.stdout)
        self.assertEqual(len(actual), len(cases))
        for case, value in zip(cases, actual):
            try:
                expected = {"result": functions[case["method"]](*case["args"])}
            except ValueError as error:
                expected = {"error": str(error)}
            with self.subTest(case=case):
                self.assertEqual(value, expected)


if __name__ == "__main__":
    unittest.main()
