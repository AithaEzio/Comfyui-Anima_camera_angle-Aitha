import { readFileSync } from "node:fs";
import { createCameraLogic } from "../js/camera_logic.js";
const data = JSON.parse(readFileSync(new URL("../js/camera_data.json", import.meta.url), "utf8"));
const logic = createCameraLogic(data);
const cases = JSON.parse(readFileSync(0, "utf8"));
const results = cases.map(({ method, args }) => {
  try { return { result: logic[method](...args) }; }
  catch (error) { return { error: error.message }; }
});
process.stdout.write(JSON.stringify(results));
