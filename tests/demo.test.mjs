import { test } from "node:test";
import assert from "node:assert/strict";
import seed from "../DEMO_DATA.json" with { type: "json" };
import {
  filterEvents,
  transitionIncident,
  answerQuery,
  prompts,
} from "../src/logic.mjs";
import { readFile } from "node:fs/promises";
test("event filters combine query, camera, severity, status and date", () => {
  assert.equal(
    filterEvents(seed.events, {
      query: "b 1234",
      camera: "CAM-07",
      severity: "medium",
      status: "new",
      date: "2026-10-01",
    }).length,
    1,
  );
  assert.equal(filterEvents(seed.events, { query: "no match" }).length, 0);
  assert.equal(filterEvents(seed.events, { date: "2026-09-30" }).length, 0);
  assert.equal(filterEvents(seed.events, {}).length, 5);
});
test("incident transitions preserve original and reject invalid statuses", () => {
  const original = seed.incidents[0];
  const changed = transitionIncident(original, "resolved");
  assert.equal(original.status, "open");
  assert.equal(changed.status, "resolved");
  assert.equal(transitionIncident(changed, "open").status, "open");
  assert.throws(() => transitionIncident(original, "deleted"));
});
test("all seeded questions return deterministic responses and valid evidence links", () => {
  for (const q of prompts) {
    const answer = answerQuery(q, seed.incidents, seed.plates);
    assert.ok(answer.text.length > 50);
    assert.ok(answer.refs.every((id) => seed.events.some((e) => e.id === id)));
    assert.deepEqual(answer, answerQuery(q, seed.incidents, seed.plates));
  }
  assert.match(
    answerQuery(prompts[0], seed.incidents, seed.plates).text,
    /Tidak ada rekaman setelah 23:00/,
  );
  assert.match(
    answerQuery(prompts[1], seed.incidents, seed.plates).text,
    /2 kendaraan/,
  );
  assert.equal(
    answerQuery("unrelated prompt", seed.incidents, seed.plates).refs.length,
    0,
  );
});
test("shift report reflects resolved incidents instead of a hardcoded total", () => {
  const resolved = seed.incidents.map((i) => transitionIncident(i, "resolved"));
  assert.match(
    answerQuery(prompts[4], resolved, seed.plates).text,
    /0 insiden aktif/,
  );
});
test("stage 2 brief exposes the final owner baseline and demo boundary", async () => {
  const html = await readFile(new URL("../public/garda-stage2.html", import.meta.url), "utf8");
  assert.match(html, /16 kanal\/titik/);
  assert.match(html, /GARDA 16 TB/);
  assert.match(html, /NVR 1 TB/);
  assert.match(html, /hot 7 hari/);
  assert.match(html, /GPU TBA/);
  assert.match(html, /feed.*sintetis/i);
});
