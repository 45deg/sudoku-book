/** Check SVG text clipping, text-to-text overlap, and connector-to-text collisions. */

import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const root = path.resolve(process.argv[2] ?? process.cwd());
const figures = path.join(root, "figures");

function svgFiles(directory) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(directory, entry.name);
    return entry.isDirectory()
      ? svgFiles(fullPath)
      : entry.isFile() && entry.name.endsWith(".svg")
        ? [fullPath]
        : [];
  });
}

const files = svgFiles(figures).sort();
if (!files.length) {
  console.log("checked 0 SVG files");
  process.exit(0);
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
const failures = [];

for (const file of files) {
  await page.goto(pathToFileURL(file).href);
  await page.locator("svg").waitFor();
  await page.evaluate(() => document.fonts?.ready);

  const collisions = await page.evaluate(() => {
    const svg = document.querySelector("svg");
    const svgBox = svg.getBoundingClientRect();
    const padding = 4;

    const boxOf = (element) => {
      const box = element.getBoundingClientRect();
      return {
        left: box.left,
        right: box.right,
        top: box.top,
        bottom: box.bottom,
        width: box.width,
        height: box.height,
      };
    };
    const textLabel = (element) =>
      element.textContent.replace(/\s+/g, " ").trim().slice(0, 80);
    const overlaps = (a, b) =>
      a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;

    const issues = [];
    const texts = [...svg.querySelectorAll("text")]
      .filter((element) => !element.hasAttribute("data-collision-ignore"))
      .map((element) => ({ element, label: textLabel(element), box: boxOf(element) }))
      .filter(({ box, label }) => label && box.width > 0 && box.height > 0);

    for (const text of texts) {
      const { box } = text;
      if (
        box.left < svgBox.left + padding ||
        box.right > svgBox.right - padding ||
        box.top < svgBox.top + padding ||
        box.bottom > svgBox.bottom - padding
      ) {
        issues.push(`text is clipped or too close to the edge: "${text.label}"`);
      }
    }

    for (let first = 0; first < texts.length; first += 1) {
      for (let second = first + 1; second < texts.length; second += 1) {
        if (overlaps(texts[first].box, texts[second].box)) {
          issues.push(
            `text overlaps text: "${texts[first].label}" / "${texts[second].label}"`,
          );
        }
      }
    }

    for (const connector of svg.querySelectorAll("[data-connector]")) {
      if (connector.hasAttribute("data-collision-ignore")) continue;
      if (typeof connector.getTotalLength !== "function") continue;
      const length = connector.getTotalLength();
      const matrix = connector.getScreenCTM();
      if (!matrix || length === 0) continue;
      const samples = Math.max(2, Math.ceil(length / 2));
      const label = connector.getAttribute("data-connector") || connector.tagName;

      for (const text of texts) {
        const box = {
          left: text.box.left - padding,
          right: text.box.right + padding,
          top: text.box.top - padding,
          bottom: text.box.bottom + padding,
        };
        let hit = false;
        for (let sample = 0; sample <= samples; sample += 1) {
          const point = connector.getPointAtLength((length * sample) / samples);
          const screen = new DOMPoint(point.x, point.y).matrixTransform(matrix);
          if (
            screen.x >= box.left &&
            screen.x <= box.right &&
            screen.y >= box.top &&
            screen.y <= box.bottom
          ) {
            hit = true;
            break;
          }
        }
        if (hit) issues.push(`connector "${label}" crosses text: "${text.label}"`);
      }
    }
    return issues;
  });

  if (collisions.length) {
    failures.push(`${path.relative(root, file)}:\n  ${collisions.join("\n  ")}`);
  }
}

await browser.close();

if (failures.length) {
  console.error(failures.join("\n\n"));
  process.exit(1);
}
console.log(`checked ${files.length} SVG files for collisions`);
