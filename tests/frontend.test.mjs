/** Browser-independent widget tests; ComfyUI and WebGL are never started. */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { createCameraLogic } from "../js/camera_logic.js";

const data = JSON.parse(readFileSync(new URL("../js/camera_data.json", import.meta.url), "utf8"));
const logic = createCameraLogic(data);

class Element {
  constructor(tag) {
    this.tagName = tag; this.children = []; this.style = {}; this.events = {}; this.hidden = false;
    this.classList = { add() {}, remove() {} }; this.value = "";
  }
  append(...items) { this.children.push(...items); }
  appendChild(item) { this.append(item); }
  replaceChildren(...items) { this.children = [...items]; }
  setAttribute(key, value) { this[key] = value; }
  addEventListener(key, handler) { this.events[key] = handler; }
  focus() { this.focused = true; }
  select() { this.selected = true; }
  queryAll(tag) { return this.children.flatMap((item) => [...(item.tagName === tag ? [item] : []), ...item.queryAll(tag)]); }
}

async function harness() {
  let extension;
  const intervals = new Map(); let nextInterval = 0;
  const context = vm.createContext({
    console: { warn() {} }, URL,
    document: { head: new Element("head"), getElementById: () => null, createElement: (tag) => new Element(tag) },
    fetch: async () => ({ ok: true, json: async () => data }),
    navigator: { clipboard: { writeText: async () => {} } },
    setInterval: (callback) => { intervals.set(++nextInterval, callback); return nextInterval; },
    clearInterval: (id) => intervals.delete(id),
  });
  const appModule = new vm.SyntheticModule(["app"], function () {
    this.setExport("app", { registerExtension(value) { extension = value; } });
  }, { context });
  const threeModule = new vm.SyntheticModule([], () => {}, { context }); // Deliberately unavailable WebGL.
  const logicModule = new vm.SourceTextModule(readFileSync(new URL("../js/camera_logic.js", import.meta.url), "utf8"), { context });
  const module = new vm.SourceTextModule(readFileSync(new URL("../js/camera_angle_widget.js", import.meta.url), "utf8"), {
    context, initializeImportMeta: (meta) => { meta.url = new URL("../js/camera_angle_widget.js", import.meta.url).href; },
  });
  await module.link((specifier) => specifier.includes("scripts/app") ? appModule : specifier.includes("three.module") ? threeModule : logicModule);
  await module.evaluate();
  return { extension, intervals, tick: () => { for (const callback of intervals.values()) callback(); } };
}
function item(name, value, type = "number") {
  return { name, value, type, computeSize: () => [100, 24], element: new Element("input") };
}
function node(type) {
  const result = {
    type, comfyClass: type, size: [350, 300], inputs: [], dom: [], properties: {}, graph: { setDirtyCanvas() {}, links: {}, getNodeById() {} },
    setSize(size) { this.size = size; },
    removeInput(slot) {
      this.inputs.splice(slot, 1);
      for (const link of Object.values(this.graph.links)) {
        if (link.target_id === this.id && link.target_slot > slot) link.target_slot--;
      }
    },
    computeSize() { return [390, this.widgets.reduce((height, current) => height + (current.computeSize?.()[1] || 0), 160)]; },
    addDOMWidget(name, type, element, options) { this.dom.push(element); const w = { name, type, options }; this.widgets.push(w); return w; },
  };
  result.widgets = type === "AithaCameraAngleNode" ? [item("horizontal_angle", 0), item("vertical_angle", 0), item("zoom", 4), item("roll", 0), item("_tags_json", "{}", "text")] : [
    item("extreme_type", "None", "combo"), item("extreme_weight", 1),
    ...data.extra_groups.flatMap((group) => [item(`${group.key}_preset`, "None", "combo"), item(`${group.key}_custom`, "", "text"), item(`${group.key}_weight`, 1)]),
  ];
  return result;
}
const get = (node, name) => node.widgets.find((w) => w.name === name);
const selectValue = (node, name, value) => { const w = get(node, name); w.value = value; w.callback?.(value); };

test("preset lookup respects circular azimuth and framing boundaries", () => {
  assert.equal(logic.closestPreset("horizontal_angle", 359).value, 0);
  assert.equal(logic.closestPreset("horizontal_angle", 181).value, 180);
  assert.equal(logic.closestPreset("vertical_angle", 30).value, 30);
  for (const preset of data.camera_presets.zoom) assert.equal(logic.closestPreset("zoom", preset.value).value, preset.value);
});

test("extra dropdowns reveal only active controls and preserve serialization types", async () => {
  const h = await harness(), extra = node("AithaCameraExtraConfigNode"); h.extension.nodeCreated(extra);
  assert.equal(get(extra, "lens_custom").hidden, true);
  assert.equal(get(extra, "lens_weight").hidden, true);
  assert.equal(get(extra, "lens_custom").type, "text");
  selectValue(extra, "lens_preset", "Fisheye distortion [Tag]");
  assert.equal(get(extra, "lens_custom").hidden, true);
  assert.equal(get(extra, "lens_weight").hidden, false);
  assert.equal(extra.dom[0].queryAll("textarea")[0].value, "fisheye");
  selectValue(extra, "lens_preset", "Custom");
  assert.equal(get(extra, "lens_custom").hidden, false);
  selectValue(extra, "lens_custom", "a custom camera caption");
  assert.equal(extra.dom[0].queryAll("textarea")[0].value, "a custom camera caption");
  selectValue(extra, "lens_preset", "None");
  assert.equal(get(extra, "lens_custom").value, "a custom camera caption");
  assert.equal(get(extra, "lens_custom").hidden, true);
  extra.onRemoved(); assert.equal(h.intervals.size, 0);
});

test("workflow restoration and external widget edits refresh extra previews", async () => {
  const h = await harness(), extra = node("AithaCameraExtraConfigNode"); h.extension.nodeCreated(extra);
  get(extra, "style_preset").value = "Sketch [Tag]";
  extra.onConfigure();
  assert.equal(extra.dom[0].queryAll("textarea")[0].value, "sketch");
  assert.equal(get(extra, "style_weight").hidden, false);
  get(extra, "style_weight").value = 2; h.tick();
  assert.equal(extra.dom[0].queryAll("textarea")[0].value, "(sketch:2.00)");
  extra.onExecuted({ extra_prompt: ["EXECUTED EXTRA PROMPT"] }); h.tick();
  assert.equal(extra.dom[0].queryAll("textarea")[0].value, "EXECUTED EXTRA PROMPT");
  extra.onRemoved();
});

test("camera dropdowns and numeric widgets remain synchronized without WebGL", async () => {
  const h = await harness(), camera = node("AithaCameraAngleNode"); h.extension.nodeCreated(camera);
  const [horizontal, vertical, zoom] = camera.dom[0].queryAll("select");
  assert.equal(horizontal.children.length, 8); assert.equal(vertical.children.length, 4); assert.equal(zoom.children.length, 6);
  horizontal.value = "270"; horizontal.events.change();
  assert.equal(get(camera, "horizontal_angle").value, 270);
  get(camera, "vertical_angle").value = 60; get(camera, "zoom").value = 10; h.tick();
  assert.equal(vertical.value, "60"); assert.equal(zoom.value, "10");
  assert.match(camera.dom[0].queryAll("textarea")[0].value, /from above/);
  assert.equal(get(camera, "_tags_json").type, "text");
  assert.equal(get(camera, "_tags_json").hidden, true);
  camera.onRemoved(); assert.equal(h.intervals.size, 0);
});

test("connected extras, settings restoration, and last executed prompts are accurate", async () => {
  const h = await harness(), camera = node("AithaCameraAngleNode"), extra = node("AithaCameraExtraConfigNode");
  h.extension.nodeCreated(extra); selectValue(extra, "lighting_preset", "Moonlight [Tag]");
  camera.inputs = [{ name: "extra_config", link: 4 }];
  camera.graph.links[4] = { origin_id: 8, origin_slot: 0 }; camera.graph.getNodeById = () => extra;
  h.extension.nodeCreated(camera);
  const preview = camera.dom[0].queryAll("textarea")[0]; assert.match(preview.value, /moonlight/);
  get(camera, "_tags_json").value = '{"azimuth":{"enabled":false}}'; camera.onConfigure();
  assert.doesNotMatch(preview.value, /straight-on/);
  camera.onExecuted({ camera_prompt: ["ACTUAL SERVER PROMPT"] }); h.tick();
  assert.equal(preview.value, "ACTUAL SERVER PROMPT");
  get(camera, "zoom").value = 8; h.tick(); assert.match(preview.value, /close-up/);
  camera.inputs.push({ name: "horizontal_angle", link: 20 }); h.tick();
  assert.equal(camera.dom[0].queryAll("select")[0].disabled, true);
  assert.match(camera.dom[0].children.at(-1).textContent, /Partial preview/);
  camera.onRemoved(); extra.onRemoved();
});

test("copy button survives asynchronous clipboard completion", async () => {
  const h = await harness(), camera = node("AithaCameraAngleNode"); h.extension.nodeCreated(camera);
  const copy = camera.dom[0].queryAll("button").find((b) => b.textContent === "Copy prompt");
  const event = { currentTarget: copy }; const pending = copy.events.click(event); event.currentTarget = null;
  await pending; assert.equal(copy.textContent, "Copied"); camera.onRemoved();
});

test("fork hooks ignore upstream nodes and prevent duplicate DOM widgets", async () => {
  const h = await harness(), upstream = node("CameraAngleNode"), camera = node("AithaCameraAngleNode");
  h.extension.nodeCreated(upstream); assert.equal(upstream.dom.length, 0);
  h.extension.nodeCreated(camera); h.extension.nodeCreated(camera);
  assert.equal(camera.dom.length, 1);
  assert.equal(get(camera, "aitha-camera-3d").serialize, false);
  assert.equal(get(camera, "aitha-camera-3d").options.serialize, false);
  assert.notEqual(get(camera, "_tags_json").serialize, false);
  const extra = node("AithaCameraExtraConfigNode"); h.extension.nodeCreated(extra);
  assert.equal(get(extra, "aitha-extra-preview").serialize, false);
  camera.onRemoved(); extra.onRemoved();
});

test("private settings stay serialized without stray sockets on creation or workflow reload", async () => {
  const h = await harness(), camera = node("AithaCameraAngleNode"); camera.id = 12;
  // Model the pre-fix socket layout: hidden settings before the real config input.
  camera.inputs = [
    { name: "_tags_json", type: "STRING", link: null, widget: { name: "_tags_json" } },
    { name: "extra_config", type: "STRING", link: 4 },
  ];
  camera.graph.links[4] = { origin_id: 8, origin_slot: 0, target_id: 12, target_slot: 1 };
  get(camera, "_tags_json").value = '{"azimuth":{"extra":2}}';
  h.extension.nodeCreated(camera);
  assert.deepEqual(camera.inputs.map((input) => input.name), ["extra_config"]);
  assert.equal(camera.inputs[0].link, 4);
  assert.equal(camera.graph.links[4].target_slot, 0);
  assert.equal(get(camera, "_tags_json").options.socketless, true);
  assert.equal(get(camera, "_tags_json").value, '{"azimuth":{"extra":2}}');
  assert.notEqual(get(camera, "_tags_json").serialize, false);
  // Configure can reintroduce a socket saved by an earlier release.
  camera.inputs.unshift({ name: "_tags_json", link: null });
  camera.graph.links[4].target_slot = 1;
  camera.onConfigure();
  assert.equal(camera.inputs.length, 2); // Wait until all saved links have loaded.
  h.extension.loadedGraphNode(camera);
  assert.deepEqual(camera.inputs.map((input) => input.name), ["extra_config"]);
  assert.equal(camera.graph.links[4].target_slot, 0);
  h.extension.loadedGraphNode(camera); // Loading cleanup is idempotent.
  assert.equal(camera.inputs[0].link, 4);
  assert.equal(get(camera, "_tags_json").hidden, true);
  camera.onRemoved();
});

test("socket cleanup preserves connected private inputs and other node types", async () => {
  const h = await harness(), camera = node("AithaCameraAngleNode");
  camera.inputs = [{ name: "_tags_json", link: 0 }, { name: "extra_config", link: 4 }];
  h.extension.nodeCreated(camera); h.extension.loadedGraphNode(camera);
  assert.equal(camera.inputs.length, 2);
  assert.equal(camera.inputs[0].link, 0);
  const upstream = node("CameraAngleNode");
  upstream.inputs = [{ name: "_tags_json", link: null }];
  h.extension.loadedGraphNode(upstream);
  assert.equal(upstream.inputs.length, 1);
  camera.onRemoved();
});
