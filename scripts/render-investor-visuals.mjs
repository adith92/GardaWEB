/**
 * GARDA Security investor screenshots (synthetic demo only).
 *
 * Captures real React routes from a locally running Vite build and places them
 * into investor-neutral 1600x900 presentation frames. No real CCTV streams,
 * government customer claims, or benchmark numbers are created.
 *
 * Run: npm ci && npx playwright install chromium && node scripts/render-investor-visuals.mjs
 */
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = process.cwd();
const visuals = path.join(root, "docs", "investor", "visuals");
const sources = path.join(visuals, "source-captures");
const renders = path.join(visuals, "renders");
const site = "http://127.0.0.1:5181";
const screens = [
  "command", "live", "playback", "events", "faces", "plates",
  "map", "incidents", "ask-garda", "analytics", "vault",
  "devices", "system", "audit", "settings",
];

await mkdir(sources, { recursive: true });
await mkdir(renders, { recursive: true });

const vite = spawn(
  process.execPath,
  [path.join(root, "node_modules", "vite", "bin", "vite.js"),
   "--host", "127.0.0.1", "--port", "5181", "--strictPort"],
  { cwd: root, stdio: ["ignore", "pipe", "pipe"] },
);
vite.stdout.on("data", chunk => process.stdout.write("[vite] " + chunk));
vite.stderr.on("data", chunk => process.stderr.write("[vite] " + chunk));
vite.on("error", error => process.stderr.write("[vite] " + error.message + "\n"));
const browser = await chromium.launch({ headless: true });

try {
  const context = await browser.newContext({
    viewport: { width: 1740, height: 980 },
    deviceScaleFactor: 1,
    locale: "id-ID",
    timezoneId: "Asia/Jakarta",
    colorScheme: "light",
  });
  const page = await context.newPage();
  let ready = false;

  for (let n = 0; n < 40; n++) {
    if (vite.exitCode !== null) throw new Error("Vite exited prematurely");
    try {
      const r = await page.goto(site + "/command", {
        waitUntil: "domcontentloaded", timeout: 4000
      });
      if (r?.ok()) { ready = true; break; }
    } catch { /* Vite may still be starting */ }
    await new Promise(resolve => setTimeout(resolve, 500));
  }
  if (!ready) throw new Error("Vite demo did not become reachable on 127.0.0.1:5181");

  const failures = [];
  for (const route of screens) {
    const response = await page.goto(site + "/" + route, {
      waitUntil: "domcontentloaded", timeout: 25000
    });
    if (!response?.ok()) throw new Error("Route unavailable: " + route);
    await page.waitForSelector(".sidebar", { timeout: 15000 });
    await page.waitForTimeout(500);

    // Investor-only screenshot adaptation. No customer/data changes to the app.
    await page.evaluate(() => {
      const replacements = [
        [/PUSADA MONITORING CENTER/gi, "GARDA SECURITY"],
        [/PUSADA HQ/gi, "GARDA HQ"],
        [/RUANG OPERASI TNI/gi, "SECURITY OPERATIONS"],
        [/PUSADA TNI/gi, "GARDA SECURITY"],
      ];
      const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walk.nextNode())) {
        if (node.parentElement?.closest("script,style")) continue;
        let value = node.nodeValue ?? "";
        for (const [from, to] of replacements) value = value.replace(from, to);
        if (value !== node.nodeValue) node.nodeValue = value;
      }
      const logo = document.querySelector(".brand img");
      if (logo) logo.style.display = "none";
      const label = document.querySelector(".nav-label");
      if (label) label.textContent = "GARDA SECURITY · DEMO";
    });
    await page.addStyleTag({
      content: ".brand img{display:none!important}.sidebar .brand{gap:4px!important}"
    });
    const filename = path.join(sources, route + ".jpg");
    await page.screenshot({
      path: filename, type: "jpeg", quality: 84,
      animations: "disabled", fullPage: false
    });
    console.log("[capture]", route, filename);
  }

  // The mobile render is the explicitly approved concept asset on main.
  const gallery = await context.newPage({
    viewport: { width: 1600, height: 1050 }
  });
  const galleryFile = path.join(visuals, "index.html");
  await gallery.goto(pathToFileURL(galleryFile).href, {
    waitUntil: "load", timeout: 30000
  });
  const count = await gallery.locator(".slide").count();
  if (count !== 19) throw new Error("Expected 19 investor slides, got " + count);

  for (let i = 0; i < count; i++) {
    await gallery.locator("#picker").selectOption(String(i));
    const active = gallery.locator(".slide.active");
    await active.waitFor({ timeout: 15000 });
    const status = await active.locator("img").evaluateAll(imgs =>
      imgs.map(img => ({ src: img.getAttribute("src"), ready: img.complete && img.naturalWidth > 0 }))
    );
    if (status.some(item => !item.ready)) {
      failures.push({ slide: i, missing: status.filter(item => !item.ready) });
      continue;
    }
    const id = await active.getAttribute("data-id");
    const filename = String(i + 1).padStart(2, "0") + "-" + id + ".jpg";
    await gallery.locator("#stage").screenshot({
      path: path.join(renders, filename), type: "jpeg",
      quality: 90, animations: "disabled",
    });
    console.log("[render]", filename);
  }
  if (failures.length) throw new Error("Missing proposal imagery: " + JSON.stringify(failures));

  console.log("Complete: 15 actual UI demo captures and 19 pitch-ready renders.");
  await context.close();
} finally {
  await browser.close();
  vite.kill("SIGTERM");
}
