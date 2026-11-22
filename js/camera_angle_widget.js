/** Comfyui-Anima_camera_angle-Aitha. See THIRD_PARTY_NOTICES.md. */
import { app } from "../../scripts/app.js";
import * as THREE from "./three.module.js";
import { createCameraLogic } from "./camera_logic.js";

const response = await fetch(new URL("./camera_data.json", import.meta.url));
if (!response.ok) throw new Error("Aitha Camera: could not load the local preset catalog.");
const data = await response.json();
const logic = createCameraLogic(data);
const CAMERA = "AithaCameraAngleNode", EXTRAS = "AithaCameraExtraConfigNode";
const widget = (node, name) => node.widgets?.find((item) => item.name === name);
const values = (node) => Object.fromEntries((node.widgets || []).map((item) => [item.name, item.value]));
const labels = {
  horizontal_angle: "Horizontal angle", vertical_angle: "Vertical angle", zoom: "Zoom", roll: "Dutch angle",
  extreme_type: "Extreme viewpoint", extreme_weight: "Viewpoint weight",
};
for (const group of data.extra_groups) {
  labels[`${group.key}_preset`] = group.label;
  labels[`${group.key}_custom`] = `${group.label} custom text`;
  labels[`${group.key}_weight`] = `${group.label} weight`;
}

// Keep the original widget type and serialization, even when its DOM is hidden.
function visibility(item, show) {
  if (!item) return;
  if (!item._aithaSize) item._aithaSize = item.computeSize || (() => [0, 24]);
  item.computeSize = show ? item._aithaSize : () => [0, -4];
  item.hidden = !show;
  if (item.element) item.element.style.display = show ? "" : "none";
  if (item.inputEl) item.inputEl.style.display = show ? "" : "none";
}
function relabel(node) {
  for (const item of node.widgets || []) if (labels[item.name]) item.label = labels[item.name];
}
function hideTagSettings(node, removeStaleSocket = false) {
  // Older workflows can restore a socket for this private, serialized widget.
  // Use LiteGraph's removal API after graph loading so real link slots follow it.
  if (removeStaleSocket) {
    for (let slot = (node.inputs?.length || 0) - 1; slot >= 0; slot--) {
      const input = node.inputs[slot];
      if (input.name === "_tags_json" && input.link == null) node.removeInput(slot);
    }
  }
  const settings = widget(node, "_tags_json");
  if (settings) {
    settings.options ??= {};
    settings.options.socketless = true;
    visibility(settings, false);
  }
}
function changed(node) { node.graph?.setDirtyCanvas(true, true); }
function button(text, onClick, title = text) {
  const result = document.createElement("button");
  result.type = "button"; result.textContent = text; result.title = title;
  result.addEventListener("click", onClick);
  return result;
}
function textElement(tag, className, text = "") {
  const result = document.createElement(tag);
  result.className = className; result.textContent = text;
  return result;
}

if (!document.getElementById("aitha-camera-style")) {
  const style = document.createElement("style");
  style.id = "aitha-camera-style";
  style.textContent = `
    .aitha-camera{box-sizing:border-box;width:100%;padding:6px;color:#e9e9ef;font:12px system-ui;display:flex;flex-direction:column;gap:8px}
    .aitha-camera *{box-sizing:border-box}
    .aitha-camera .viewport{position:relative;width:100%;aspect-ratio:1.2;min-height:250px;max-height:440px;border:1px solid #38384d;border-radius:8px;overflow:hidden;background:#10101a}
    .aitha-camera canvas{display:block;width:100%;height:100%;touch-action:none;cursor:grab}
    .aitha-camera canvas:active{cursor:grabbing}
    .aitha-camera .overlay{position:absolute;top:8px;left:10px;right:10px;pointer-events:none;color:#c8c8db;text-shadow:0 1px 3px #000;font-size:11px}
    .aitha-camera .selects{display:grid;grid-template-columns:1fr;gap:6px}
    .aitha-camera .select-row{display:grid;grid-template-columns:65px minmax(0,1fr) 48px;gap:6px;align-items:center}
    .aitha-camera select,.aitha-camera button,.aitha-camera input,.aitha-camera textarea{font:inherit;color:inherit;background:#20202d;border:1px solid #4b4b60;border-radius:4px;padding:4px 6px;min-width:0}
    .aitha-camera button{cursor:pointer}
    .aitha-camera button:hover{background:#333347}
    .aitha-camera :focus-visible{outline:2px solid #b0a1ff;outline-offset:2px}
    .aitha-camera .horizontal{color:#ffa2c4}.aitha-camera .vertical{color:#75ead6}.aitha-camera .distance{color:#ffd279}
    .aitha-camera output{font:11px ui-monospace,monospace;text-align:right}
    .aitha-camera .actions{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
    .aitha-camera .hint{font-size:11px;color:#b0b0c2;line-height:1.5}
    .aitha-camera .preview{width:100%;resize:vertical;min-height:55px;max-height:160px;font:11px ui-monospace,monospace;line-height:1.5;color:#fff0b0}
    .aitha-camera .settings{max-height:380px;overflow:auto;border:1px solid #414156;padding:8px;border-radius:6px}
    .aitha-camera fieldset{border:1px solid #414156;padding:8px;margin:6px 0;border-radius:4px}
    .aitha-camera legend{padding:0 5px;color:#cabfff}
    .aitha-camera .field{display:flex;gap:6px;align-items:center;margin:5px 0}
    .aitha-camera .field>span{min-width:90px}.aitha-camera .field input[type=text]{flex:1;width:0}
    .aitha-camera .field input[type=number]{width:80px}.aitha-camera .field input[type=checkbox]{accent-color:#a99aff}
    .aitha-camera .error{color:#ffb0a8}
  `;
  document.head.appendChild(style);
}

function attachExtras(node) {
  relabel(node);
  const container = textElement("div", "aitha-camera");
  const preview = textElement("textarea", "preview");
  preview.readOnly = true; preview.rows = 3; preview.setAttribute("aria-label", "Extra prompt preview");
  const hint = textElement("div", "hint", "None skips a group. Custom reveals your text field. Tag = booru vocabulary; Description = English caption.");
  container.append(hint, preview);
  const domWidget = node.addDOMWidget("aitha-extra-preview", "aitha-extra-preview", container, { serialize: false, hideOnZoom: false, getMinHeight: () => 120 });
  domWidget.serialize = false;
  let lastState = "";
  function refresh(resize = false) {
    const state = values(node);
    let sizeChanged = false;
    const setVisible = (name, visible) => {
      const item = widget(node, name);
      if (item && item.hidden === visible) sizeChanged = true;
      visibility(item, visible);
    };
    setVisible("extreme_weight", state.extreme_type !== "None");
    for (const group of data.extra_groups) {
      setVisible(`${group.key}_custom`, state[`${group.key}_preset`] === "Custom");
      setVisible(`${group.key}_weight`, state[`${group.key}_preset`] !== "None");
    }
    try {
      preview.value = logic.extraPrompt(logic.buildExtraConfig(state)) || "No extra prompts selected.";
      preview.classList.remove("error");
    } catch (error) { preview.value = error.message; preview.classList.add("error"); }
    if (resize || sizeChanged) {
      const minimum = node.computeSize();
      node.setSize([Math.max(node.size[0], 390), minimum[1]]);
      changed(node);
    }
    lastState = JSON.stringify(state);
  }
  for (const item of node.widgets || []) {
    if (!item.name.endsWith("_preset") && !["extreme_type", "extreme_weight"].includes(item.name) && !item.name.endsWith("_custom") && !item.name.endsWith("_weight")) continue;
    const original = item.callback;
    item.callback = function (...args) { const result = original?.apply(this, args); refresh(); return result; };
  }
  const configure = node.onConfigure;
  node.onConfigure = function (...args) { const result = configure?.apply(this, args); refresh(true); return result; };
  const executed = node.onExecuted;
  node.onExecuted = function (message) {
    executed?.apply(this, arguments);
    if (message?.extra_prompt?.[0] !== undefined) preview.value = message.extra_prompt[0] || "No extra prompts selected.";
  };
  const interval = setInterval(() => {
    // Programmatic widget updates can bypass callbacks.
    if (JSON.stringify(values(node)) !== lastState) refresh();
  }, 200);
  const remove = node.onRemoved;
  node.onRemoved = function (...args) { clearInterval(interval); return remove?.apply(this, args); };
  refresh(true);
}

function attachCamera(node) {
  relabel(node);
  hideTagSettings(node, true);
  let tagSettings = logic.settings(widget(node, "_tags_json")?.value || "{}");
  const container = textElement("div", "aitha-camera");
  const viewport = textElement("div", "viewport");
  const overlay = textElement("div", "overlay", "Drag pink: horizontal · cyan: vertical · gold: zoom");
  const selectors = textElement("div", "selects"), controls = new Map();
  const preview = textElement("textarea", "preview");
  preview.readOnly = true; preview.rows = 3; preview.setAttribute("aria-label", "Camera prompt preview");
  const status = textElement("div", "hint"); status.setAttribute("role", "status");
  const settingsPanel = textElement("div", "settings"); settingsPanel.hidden = true;
  const actions = textElement("div", "actions");
  container.append(viewport, selectors, actions, settingsPanel, preview, status);
  const domWidget = node.addDOMWidget("aitha-camera-3d", "aitha-camera-3d", container, {
    serialize: false, hideOnZoom: false,
    getMinHeight: () => Math.ceil(Math.max(250, Math.min(440, (node.size[0] - 20) / 1.2)) + 260 + (settingsPanel.hidden ? 0 : 390)),
    getMaxHeight: () => 1400,
  });
  domWidget.serialize = false;
  node.setSize([Math.max(node.size[0], 400), Math.max(node.size[1], 690)]);
  const state = () => logic.normalizeCamera(widget(node, "horizontal_angle")?.value, widget(node, "vertical_angle")?.value, widget(node, "zoom")?.value, widget(node, "roll")?.value);
  let updateScene = () => {}, lastSignature = "", disposed = false;
  function setValue(key, value) {
    const item = widget(node, key);
    if (!item || node.inputs?.some((input) => input.name === key && input.link != null)) return;
    item.value = value;
    item.callback?.call(item, value);
    changed(node);
    refresh(true);
  }
  for (const [key, label, color] of [["horizontal_angle", "Horizontal", "horizontal"], ["vertical_angle", "Vertical", "vertical"], ["zoom", "Distance", "distance"]]) {
    const row = textElement("label", `select-row ${color}`), select = document.createElement("select");
    select.setAttribute("aria-label", `${label} camera preset`);
    for (const preset of data.camera_presets[key]) {
      const option = document.createElement("option"); option.value = String(preset.value); option.textContent = preset.label;
      select.append(option);
    }
    const output = document.createElement("output");
    row.append(textElement("span", "", label), select, output); selectors.append(row);
    select.addEventListener("change", () => setValue(key, Number(select.value)));
    controls.set(key, { select, output });
  }
  actions.append(button("Reset camera", () => {
    for (const [key, value] of Object.entries(logic.normalizeCamera())) setValue(key, value);
  }));
  const settingsButton = button("Edit tags and weights", () => {
    settingsPanel.hidden = !settingsPanel.hidden;
    settingsButton.textContent = settingsPanel.hidden ? "Edit tags and weights" : "Hide settings";
    node.setSize([node.size[0], Math.max(690, node.size[1] + (settingsPanel.hidden ? -390 : 390))]);
    changed(node);
  });
  actions.append(settingsButton, button("Copy prompt", async (event) => {
    const target = event.currentTarget;
    try {
      await navigator.clipboard.writeText(preview.value);
      target.textContent = "Copied";
    } catch { preview.focus(); preview.select(); status.textContent = "Press Ctrl+C to copy the selected prompt."; }
  }));
  function saveSettings() {
    widget(node, "_tags_json").value = JSON.stringify(tagSettings);
    changed(node); refresh(true);
  }
  function settingField(parent, title, target, key, type = "text", min, max, step) {
    const row = textElement("label", "field"), input = document.createElement("input");
    input.type = type; input.setAttribute("aria-label", title);
    if (type === "checkbox") input.checked = target[key]; else input.value = target[key];
    if (min !== undefined) input.min = min;
    if (max !== undefined) input.max = max;
    if (step !== undefined) input.step = step;
    input.addEventListener(type === "text" ? "input" : "change", () => {
      target[key] = type === "checkbox" ? input.checked : type === "number" ? logic.number(input.value, target[key], min, max) : input.value;
      if (type === "number") input.value = target[key];
      saveSettings();
    });
    row.append(textElement("span", "", title), input); parent.append(row);
  }
  function buildSettings() {
    settingsPanel.replaceChildren();
    settingsPanel.append(textElement("div", "hint", "Weights change prompt emphasis. The upstream angle multiplier defaults to 10; tune it for your checkpoint. Reset camera keeps these settings."));
    settingField(settingsPanel, "Use angle multiplier", tagSettings, "xy_mult_enabled", "checkbox");
    settingField(settingsPanel, "Angle multiplier", tagSettings, "xy_mult", "number", 0.1, 50, 0.1);
    settingField(settingsPanel, "Extra weight scale", tagSettings, "extra_master", "number", 0, 20, 0.1);
    for (const [axis, name] of [["azimuth", "Horizontal tags"], ["elevation", "Vertical tags"], ["distance", "Framing tags"], ["tilt", "Tilt tag"]]) {
      const group = document.createElement("fieldset"); group.append(textElement("legend", "", name));
      settingField(group, "Enabled", tagSettings[axis], "enabled", "checkbox");
      settingField(group, "Extra weight", tagSettings[axis], "extra", "number", -50, 50, 0.1);
      if (axis === "azimuth") {
        settingField(group, "Base weight", tagSettings.azimuth, "weight", "number", 0.1, 50, 0.1);
        for (const [key, value] of Object.entries(tagSettings.azimuth.directions)) settingField(group, key[0].toUpperCase() + key.slice(1), value, "tag");
      } else if (axis === "tilt") settingField(group, "Dutch angle", tagSettings.tilt, "dutch_tag");
      else {
        const names = { high: "From above", eye: "Eye level", low: "From below", ecu: "Extreme close-up", cu: "Close-up", medium: "Medium shot", cowboy_shot: "Cowboy shot", full: "Full body", wide: "Wide shot" };
        for (const [key, value] of Object.entries(tagSettings[axis].categories)) settingField(group, names[key] || key, value, "tag");
      }
      settingsPanel.append(group);
    }
    settingsPanel.append(button("Reset all tags and weights", () => { tagSettings = logic.settings(); saveSettings(); buildSettings(); }));
  }
  buildSettings();
  function connectedExtras() {
    const input = node.inputs?.find((item) => item.name === "extra_config");
    if (input?.link == null) return { config: "", unknown: false };
    const link = node.graph?.links?.[input.link];
    const origin = node.graph?.getNodeById(link?.origin_id);
    if ((origin?.comfyClass === EXTRAS || origin?.type === EXTRAS) && link?.origin_slot === 0) {
      return { config: logic.buildExtraConfig(values(origin)), unknown: origin.inputs?.some((item) => item.link != null) || false };
    }
    return { config: "", unknown: true };
  }
  function refresh(force = false) {
    if (disposed) return;
    const camera = state();
    try {
      const extra = connectedExtras();
      const rawTags = widget(node, "_tags_json")?.value || "{}";
      const signature = JSON.stringify([camera, rawTags, extra, node.inputs?.map((input) => [input.name, input.link])]);
      if (!force && signature === lastSignature) return;
      lastSignature = signature;
      for (const [key, control] of controls) {
        const linked = node.inputs?.some((input) => input.name === key && input.link != null);
        control.select.disabled = linked;
        control.select.title = linked ? "This value is supplied by a connected input. Run the workflow to see its prompt." : "Choose a preset or adjust the numeric widget / 3D handle.";
        control.select.value = String(logic.closestPreset(key, camera[key]).value);
        control.output.textContent = key === "zoom" ? camera[key].toFixed(1) : `${Math.round(camera[key])}°`;
      }
      preview.value = logic.cameraPrompt(camera.horizontal_angle, camera.vertical_angle, camera.zoom, camera.roll, rawTags, extra.config);
      preview.classList.remove("error");
      const linkedCamera = ["horizontal_angle", "vertical_angle", "zoom", "roll"].some((key) => node.inputs?.some((input) => input.name === key && input.link != null));
      status.textContent = extra.unknown || linkedCamera ? "Partial preview: run the workflow to include values from connected inputs." : "Live prompt preview · 3D guide only. Connect camera_prompt to your prompt text chain.";
      if (extra.config?.extreme) status.textContent += " The extreme viewpoint replaces horizontal and vertical prompt tags.";
      overlay.textContent = `${logic.closestPreset("horizontal_angle", camera.horizontal_angle).label} · ${Math.round(camera.horizontal_angle)}° / ${Math.round(camera.vertical_angle)}°`;
      updateScene(camera);
    } catch (error) { preview.value = error.message; preview.classList.add("error"); }
  }
  const configure = node.onConfigure;
  node.onConfigure = function (...args) {
    const result = configure?.apply(this, args);
    hideTagSettings(node);
    try { tagSettings = logic.settings(widget(node, "_tags_json")?.value || "{}"); buildSettings(); }
    catch (error) { status.textContent = error.message; }
    refresh(true); return result;
  };
  const executed = node.onExecuted;
  node.onExecuted = function (message) {
    executed?.apply(this, arguments);
    if (message?.camera_prompt?.[0] !== undefined) {
      preview.value = message.camera_prompt[0]; preview.classList.remove("error");
      status.textContent = "Prompt from the last execution. Changing a camera setting restores the live preview.";
    }
  };
  let cleanupScene = () => {};
  try {
    const scene = createScene(viewport, state, setValue);
    updateScene = scene.update; cleanupScene = scene.dispose;
  } catch (error) {
    viewport.append(textElement("div", "hint error", "3D rendering is unavailable. Use the dropdowns or numeric widgets."));
    console.warn("[Aitha Camera] Could not initialize WebGL:", error);
  }
  viewport.append(overlay);
  const interval = setInterval(() => refresh(), 100);
  const remove = node.onRemoved;
  node.onRemoved = function (...args) {
    disposed = true; clearInterval(interval); cleanupScene(); return remove?.apply(this, args);
  };
  refresh(true);
  node.setSize([node.size[0], Math.max(node.size[1], node.computeSize()[1])]);
}

function createScene(viewport, getState, setValue) {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  viewport.append(renderer.domElement);
  const canvas = renderer.domElement, scene = new THREE.Scene(); scene.background = new THREE.Color(0x10101a);
  const camera = new THREE.PerspectiveCamera(45, 1.2, 0.1, 100);
  camera.position.set(4, 3, 4); camera.lookAt(0, 0.5, 0);
  const center = new THREE.Vector3(0, 0.5, 0), radius = 1.8, elevationRadius = 1.4;
  scene.add(new THREE.AmbientLight(0xffffff, 1.2));
  const light = new THREE.DirectionalLight(0xffffff, 2); light.position.set(4, 7, 5); scene.add(light);
  scene.add(new THREE.GridHelper(5, 20, 0x38384b, 0x242434));
  function material(color) { return new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.2 }); }
  function handle(color) { const result = new THREE.Mesh(new THREE.SphereGeometry(0.14, 20, 16), material(color)); scene.add(result); return result; }
  const horizontal = handle(0xe95b98), vertical = handle(0x46dfcb), distance = handle(0xffc54d);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(radius, 0.025, 8, 80), new THREE.MeshBasicMaterial({ color: 0xe95b98 }));
  ring.rotation.x = Math.PI / 2; scene.add(ring);
  const points = [];
  for (let i = 0; i <= 40; i++) { const angle = (-30 + 90 * i / 40) * Math.PI / 180; points.push(new THREE.Vector3(-0.8, center.y + elevationRadius * Math.sin(angle), elevationRadius * Math.cos(angle))); }
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), new THREE.LineBasicMaterial({ color: 0x46dfcb })));
  const card = new THREE.Mesh(new THREE.BoxGeometry(1.1, 1.3, 0.04), material(0x5c577e)); card.position.copy(center); scene.add(card);
  // A simple face establishes the subject's front without downloading assets.
  const face = new THREE.Mesh(new THREE.CircleGeometry(0.17, 24), new THREE.MeshBasicMaterial({ color: 0xe9dbea })); face.position.set(0, 0.76, 0.025); scene.add(face);
  const body = new THREE.Mesh(new THREE.CircleGeometry(0.3, 24), new THREE.MeshBasicMaterial({ color: 0xb39ee0 })); body.scale.set(1, 1.3, 1); body.position.set(0, 0.24, 0.025); scene.add(body);
  const indicator = new THREE.Mesh(new THREE.ConeGeometry(0.13, 0.32, 4), material(0xe95b98)); scene.add(indicator);
  const lineGeometry = new THREE.BufferGeometry().setFromPoints([center, new THREE.Vector3()]);
  const line = new THREE.Line(lineGeometry, new THREE.LineBasicMaterial({ color: 0xffc54d })); scene.add(line);
  function render() { renderer.render(scene, camera); }
  function update(state) {
    const azimuth = state.horizontal_angle * Math.PI / 180, elevation = state.vertical_angle * Math.PI / 180;
    const extent = 2.6 - state.zoom / 10 * 2;
    const target = new THREE.Vector3(extent * Math.sin(azimuth) * Math.cos(elevation), center.y + extent * Math.sin(elevation), extent * Math.cos(azimuth) * Math.cos(elevation));
    indicator.position.copy(target); indicator.lookAt(center); indicator.rotateX(Math.PI / 2); indicator.rotateY(state.roll * Math.PI / 6);
    horizontal.position.set(radius * Math.sin(azimuth), 0.12, radius * Math.cos(azimuth));
    vertical.position.set(-0.8, center.y + elevationRadius * Math.sin(elevation), elevationRadius * Math.cos(elevation));
    distance.position.lerpVectors(center, target, 0.6);
    const positions = lineGeometry.attributes.position;
    positions.setXYZ(0, center.x, center.y, center.z); positions.setXYZ(1, target.x, target.y, target.z); positions.needsUpdate = true;
    lineGeometry.computeBoundingSphere(); render();
  }
  const resize = new ResizeObserver(() => {
    const width = Math.max(1, viewport.clientWidth), height = Math.max(1, viewport.clientHeight);
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix(); render();
  });
  resize.observe(viewport);
  const raycaster = new THREE.Raycaster(), pointer = new THREE.Vector2(), handles = [horizontal, vertical, distance];
  let dragging = null, lastY = 0;
  const events = new AbortController();
  function ray(event) {
    const bounds = canvas.getBoundingClientRect();
    pointer.set((event.clientX - bounds.left) / bounds.width * 2 - 1, -(event.clientY - bounds.top) / bounds.height * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
  }
  canvas.addEventListener("pointerdown", (event) => {
    ray(event);
    const hits = raycaster.intersectObjects(handles);
    if (!hits.length) return;
    dragging = hits[0].object; lastY = event.clientY; canvas.setPointerCapture(event.pointerId); event.preventDefault(); event.stopPropagation();
  }, { signal: events.signal });
  canvas.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    ray(event);
    const point = new THREE.Vector3(), plane = new THREE.Plane();
    if (dragging === horizontal) {
      plane.setFromNormalAndCoplanarPoint(new THREE.Vector3(0, 1, 0), new THREE.Vector3());
      if (raycaster.ray.intersectPlane(plane, point)) setValue("horizontal_angle", (Math.atan2(point.x, point.z) * 180 / Math.PI + 360) % 360);
    } else if (dragging === vertical) {
      plane.setFromNormalAndCoplanarPoint(new THREE.Vector3(1, 0, 0), new THREE.Vector3(-0.8, 0, 0));
      if (raycaster.ray.intersectPlane(plane, point)) setValue("vertical_angle", Math.max(-30, Math.min(60, Math.atan2(point.y - center.y, point.z) * 180 / Math.PI)));
    } else setValue("zoom", Math.max(0, Math.min(10, getState().zoom - (event.clientY - lastY) * 0.05)));
    lastY = event.clientY; event.preventDefault(); event.stopPropagation();
  }, { signal: events.signal });
  const release = () => { dragging = null; };
  for (const event of ["pointerup", "pointercancel", "lostpointercapture"]) canvas.addEventListener(event, release, { signal: events.signal });
  // Capture at window level because newer graph canvases intercept wheel events.
  window.addEventListener("wheel", (event) => {
    if (!event.composedPath().includes(canvas) || !event.deltaY) return;
    event.preventDefault(); event.stopPropagation();
    setValue("zoom", Math.max(0, Math.min(10, getState().zoom + (event.deltaY < 0 ? 0.25 : -0.25))));
  }, { capture: true, passive: false, signal: events.signal });
  update(getState());
  return {
    update,
    dispose() {
      events.abort(); resize.disconnect();
      scene.traverse((object) => { object.geometry?.dispose(); const materials = Array.isArray(object.material) ? object.material : [object.material]; for (const item of materials) item?.dispose(); });
      renderer.dispose(); renderer.forceContextLoss(); canvas.remove();
    },
  };
}

app.registerExtension({
  name: "Aitha.AnimaCameraAngle",
  loadedGraphNode(node) {
    if ((node.comfyClass || node.type) === CAMERA) hideTagSettings(node, true);
  },
  nodeCreated(node) {
    const type = node.comfyClass || node.type;
    if (![CAMERA, EXTRAS].includes(type) || node._aithaCameraAttached) return;
    node._aithaCameraAttached = true;
    if (type === CAMERA) attachCamera(node); else attachExtras(node);
  },
});
