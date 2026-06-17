#!/usr/bin/env node
// forensic-audit.mjs — five-stage forensic technical due-diligence pipeline.
// Drives headless `claude -p` subagents; emits audit/01..05.md (structured, machine-checkable).
// Nothing about the target is hardcoded: paths/branch/build commands are discovered at runtime.
// Substrate proven by preflight: claude -p authenticates (host OAuth), root => acceptEdits perm mode.
//
// Usage:
//   node audit/forensic-audit.mjs            # resume from first incomplete stage
//   node audit/forensic-audit.mjs --fresh    # tear down audit outputs and start at stage 1
//   node audit/forensic-audit.mjs --preflight# prove auth + tool-use + file-handoff, then exit
//   node audit/forensic-audit.mjs --stage N  # run only stage N (1..5); requires prior artifacts

import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, readFileSync, existsSync, rmSync, appendFileSync } from "node:fs";
import { join, resolve } from "node:path";

// ───────────────────────────── config / paths ─────────────────────────────
const REPO = resolve(process.cwd());
const AUDIT = join(REPO, "audit");
const WORK = join(AUDIT, ".work");
const LOG = join(WORK, "run.log");
const STATE = join(WORK, "state.json");
const ARGS = process.argv.slice(2);
const FLAG = (n) => ARGS.includes(n);
const ARGVAL = (n) => { const i = ARGS.indexOf(n); return i >= 0 ? ARGS[i + 1] : null; };

// Workhorse vs. deep-reasoning vs. web models. (Aliases resolve in this env.)
const M = { fast: "sonnet", deep: "opus", web: "sonnet" };

// The five global invariants — appended to every worker's system prompt, verbatim in spirit.
const INVARIANTS = [
  "FORENSIC AUDIT — GLOBAL INVARIANTS (obey all, every turn):",
  "1. Absence of evidence is not evidence of absence. Never claim a thing does not exist / is unused / is unreachable unless you name where you looked and that search space is the full Stage-1 surface. Otherwise record it as 'unverified', never 'absent'.",
  "2. No claim without a location. Every finding/behavior/assertion cites a concrete path:line (or a named artifact) a reviewer can open. Drop any claim without a citable anchor.",
  "3. Coverage has a denominator and visitation must be evidenced. Actually Read/Grep the files you classify or audit. Do not self-report visitation you did not perform.",
  "4. Verification is adversarial, not self-review. When asked to falsify, genuinely try to REFUTE each claim against the source; do not rubber-stamp.",
  "5. Mutation is a means, not a deliverable. You may modify/instrument/install/run code in this sandbox, but the ONLY deliverable is the JSON artifact you Write. Never git commit or git push.",
  "6. Never exfiltrate sensitive data. Reference secrets/PII/PHI/credentials by path + category only; never paste their contents into your output.",
].join("\n");

let BRANCH = "HEAD", SEQ = 0, TOTAL_COST = 0;

// ───────────────────────────── small utilities ─────────────────────────────
const j = (x) => JSON.stringify(x);
const jp = (x) => JSON.stringify(x, null, 2);
const nowts = () => new Date().toISOString();
function log(s) { const line = "[" + nowts() + "] " + s; console.log(line); try { appendFileSync(LOG, line + "\n"); } catch {} }
function loadJson(p) { try { return JSON.parse(readFileSync(p, "utf8")); } catch { return null; } }
function saveJson(p, o) { writeFileSync(p, jp(o)); }

function sh(cmd, args, opts = {}) {
  return new Promise((res) => {
    const p = spawn(cmd, args, { cwd: REPO, ...opts });
    let O = "", E = "";
    p.stdout?.on("data", (d) => (O += d));
    p.stderr?.on("data", (d) => (E += d));
    p.on("close", (code) => res({ code, out: O, err: E }));
    p.on("error", (e) => res({ code: -1, out: O, err: String(e) }));
  });
}

// bounded-concurrency parallel barrier
async function pMap(xs, fn, n = 3) {
  const out = []; let i = 0;
  await Promise.all(Array(Math.min(n, xs.length)).fill(0).map(async () => {
    while (i < xs.length) { const k = i++; out[k] = await fn(xs[k], k); }
  }));
  return out;
}

// ───────────────────────────── mini JSON-Schema validator ─────────────────────────────
// Supports: type(object/array/string/number/integer/boolean), required[], properties{}, items{}, minItems, enum[].
function validate(schema, data, path = "$", errs = []) {
  if (!schema) return errs;
  const t = schema.type;
  if (t) {
    const ok =
      t === "object" ? data && typeof data === "object" && !Array.isArray(data) :
      t === "array" ? Array.isArray(data) :
      t === "string" ? typeof data === "string" :
      t === "number" ? typeof data === "number" :
      t === "integer" ? Number.isInteger(data) :
      t === "boolean" ? typeof data === "boolean" : true;
    if (!ok) { errs.push(path + ": expected " + t + ", got " + (Array.isArray(data) ? "array" : typeof data)); return errs; }
  }
  if (schema.enum && !schema.enum.includes(data)) errs.push(path + ": '" + data + "' not in enum " + j(schema.enum));
  if (t === "object" && data && typeof data === "object" && !Array.isArray(data)) {
    for (const r of schema.required || []) if (!(r in data)) errs.push(path + "." + r + ": required");
    for (const [k, sub] of Object.entries(schema.properties || {})) if (k in data) validate(sub, data[k], path + "." + k, errs);
  }
  if (t === "array" && Array.isArray(data)) {
    if (schema.minItems != null && data.length < schema.minItems) errs.push(path + ": minItems " + schema.minItems + ", got " + data.length);
    if (schema.items) data.forEach((el, i2) => validate(schema.items, el, path + "[" + i2 + "]", errs));
  }
  return errs;
}

// ───────────────────────────── claude -p worker driver ─────────────────────────────
// stream-json so we can EVIDENCE visitation from real tool activity (not self-report).
function parseStream(out) {
  let envelope = null, toolText = "", toolPaths = new Set(), bashCmds = [];
  for (const line of out.split("\n")) {
    const s = line.trim(); if (!s) continue;
    let o; try { o = JSON.parse(s); } catch { continue; }
    if (o.type === "result") envelope = o;
    const content = o?.message?.content;
    if (Array.isArray(content)) for (const b of content) {
      if (b?.type === "tool_use") {
        toolText += " " + j(b.input || {});
        const fp = b.input?.file_path || b.input?.path || b.input?.notebook_path;
        if (fp) toolPaths.add(String(fp));
        if (b.name === "Bash" && b.input?.command) bashCmds.push(String(b.input.command));
      }
    }
  }
  return { envelope, toolText, toolPaths: [...toolPaths], bashCmds };
}

async function runAgent({ name, prompt, schema, model = M.fast, maxTurns = 50, web = false, timeoutMs = 9e5 }) {
  const tag = name.replace(/\W+/g, "_") + "_" + SEQ++;
  const out = join(WORK, "a_" + tag + ".json");
  const tools = (web ? "Read,Grep,Glob,Bash,WebSearch,WebFetch" : "Read,Grep,Glob,Bash") + ",Write";
  const full = prompt +
    "\n\nOUTPUT CONTRACT: Use the Write tool to put ONLY raw JSON (no prose, no markdown fence) conforming to this JSON Schema:\n" +
    j(schema) + "\nWrite it to exactly this path: " + out + "\nThe JSON file you Write is your sole deliverable.";
  const args = ["-p", full, "--output-format", "stream-json", "--verbose", "--model", model,
    "--max-turns", String(maxTurns), "--allowedTools", tools, "--add-dir", REPO,
    "--strict-mcp-config", "--permission-mode", "acceptEdits", "--append-system-prompt", INVARIANTS];
  const t0 = Date.now();
  const r = await new Promise((res) => {
    const p = spawn("claude", args, { cwd: REPO, stdio: ["ignore", "pipe", "pipe"] });
    let O = "", E = "";
    const k = setTimeout(() => { try { p.kill("SIGKILL"); } catch {} }, timeoutMs);
    p.stdout.on("data", (d) => (O += d));
    p.stderr.on("data", (d) => (E += d));
    p.on("close", () => { clearTimeout(k); res({ O, E }); });
    p.on("error", () => { clearTimeout(k); res({ O, E }); });
  });
  const { envelope, toolText, toolPaths, bashCmds } = parseStream(r.O);
  const cost = Number(envelope?.total_cost_usd || 0); TOTAL_COST += cost;
  const data = existsSync(out) ? loadJson(out) : null;
  const secs = ((Date.now() - t0) / 1000).toFixed(0);
  log("    · " + name + " [" + model + "] " + secs + "s $" + cost.toFixed(3) +
    " tools:" + toolPaths.length + " bash:" + bashCmds.length + (data ? "" : " NO-OUTPUT"));
  return { ok: !!data, data, toolText, toolPaths, bashCmds, cost, raw: r.O.slice(-400) };
}

// run + validate, with one corrective retry on schema failure
async function agentValidated(opts) {
  let lastErr = "no-output";
  for (let attempt = 1; attempt <= 2; attempt++) {
    const r = await runAgent({ ...opts, name: attempt === 1 ? opts.name : opts.name + "_retry",
      prompt: attempt === 1 ? opts.prompt
        : opts.prompt + "\n\nNOTE: your previous attempt FAILED schema validation with: " + lastErr + "\nRe-emit corrected JSON that satisfies every required field." });
    if (!r.ok) { lastErr = r.err || "no-structured-output"; continue; }
    const errs = validate(opts.schema, r.data);
    if (errs.length === 0) return r;
    lastErr = errs.slice(0, 10).join("; ");
    log("    ⚠ " + opts.name + " schema errs: " + lastErr);
  }
  return { ok: false, err: "schema-failed: " + lastErr, toolText: "", toolPaths: [], bashCmds: [] };
}

// ───────────────────────────── persistence / checkpoint / halt ─────────────────────────────
async function gitCheckpoint(stage) {
  await sh("git", ["add", "-A", "audit"]);
  const msg = "audit: " + stage;
  const c = await sh("git", ["-c", "user.name=claude-forensic-audit", "-c", "user.email=noreply@anthropic.com", "commit", "-m", msg]);
  if (c.code !== 0 && !/nothing to commit/.test(c.out + c.err)) log("    (git commit: " + (c.err || c.out).trim().split("\n")[0] + ")");
  for (let a = 0; a < 4; a++) {
    const p = await sh("git", ["push", "-u", "origin", BRANCH]);
    if (p.code === 0) { log("    ↑ pushed " + stage + " to " + BRANCH); return; }
    log("    (push attempt " + (a + 1) + " failed: " + (p.err || p.out).trim().split("\n").slice(-1)[0] + ")");
    await new Promise((r) => setTimeout(r, 2000 * 2 ** a));
  }
  log("    (push failed after retries — artifacts remain committed locally)");
}

function readState() { return loadJson(STATE) || { completed: {}, started: nowts() }; }
async function checkpoint(stageKey, mdName, md, jsonName, obj) {
  writeFileSync(join(AUDIT, mdName), md);
  saveJson(join(WORK, jsonName), obj);
  const st = readState(); st.completed[stageKey] = nowts(); st.total_cost_api_equiv = Number(TOTAL_COST.toFixed(2)); saveJson(STATE, st);
  await gitCheckpoint(stageKey);
}
async function halt(stageKey, why) {
  log("HALT at " + stageKey + ": " + why);
  const md = "# HALT REPORT — " + stageKey + "\n\nThe pipeline stopped rather than emit a confident-but-unverified artifact.\n\n**Stage:** " + stageKey + "\n\n**Reason:**\n\n" + why + "\n\n_Generated " + nowts() + "._\n";
  writeFileSync(join(AUDIT, "HALT-REPORT.md"), md);
  const st = readState(); st.halt = { stageKey, why, at: nowts() }; saveJson(STATE, st);
  await gitCheckpoint("HALT-" + stageKey);
  process.exit(2);
}

// ───────────────────────────── shared schema fragments ─────────────────────────────
const ROLE_ENUM = ["source", "test", "doc", "config", "asset", "generated", "dead", "unknown"];
const CLASS_ENUM = ["bug", "security", "doc-drift", "design-defect", "code-intent-mismatch", "perf", "other"];
const SEV_ENUM = ["critical", "high", "medium", "low", "info"];
const auditFindingsSchema = {
  type: "object", required: ["findings"], properties: {
    findings: { type: "array", items: { type: "object",
      required: ["title", "location", "class", "severity", "evidence", "intent_link"],
      properties: {
        title: { type: "string" }, location: { type: "string" },
        class: { type: "string", enum: CLASS_ENUM }, severity: { type: "string", enum: SEV_ENUM },
        evidence: { type: "string" }, intent_link: { type: "string" } } } } } };

// ───────────────────────────── filesystem denominator ─────────────────────────────
async function enumerateDenominator() {
  const tracked = (await sh("git", ["ls-files"])).out.split("\n").map((s) => s.trim()).filter(Boolean);
  const untracked = (await sh("git", ["ls-files", "--others", "--exclude-standard"])).out.split("\n").map((s) => s.trim()).filter(Boolean);
  const all = [...new Set([...tracked, ...untracked])].filter((p) => !p.startsWith("audit/")).sort();
  return all;
}

// ════════════════════════════════ STAGE 1 ════════════════════════════════
async function stage1() {
  log("STAGE 1 — comprehensive understanding");
  const denom = await enumerateDenominator();
  saveJson(join(WORK, "denominator.json"), denom);
  log("  denominator: " + denom.length + " files (excl. audit/)");

  const schema = {
    type: "object", required: ["files", "entry_points", "architecture", "provisional_intent", "coverage"],
    properties: {
      files: { type: "array", minItems: 1, items: { type: "object", required: ["path", "role", "note"],
        properties: { path: { type: "string" }, role: { type: "string", enum: ROLE_ENUM }, note: { type: "string" } } } },
      entry_points: { type: "array", items: { type: "object", required: ["name", "kind", "location", "description"],
        properties: { name: { type: "string" }, kind: { type: "string" }, location: { type: "string" }, description: { type: "string" } } } },
      architecture: { type: "string" },
      provisional_intent: { type: "string" },
      coverage: { type: "object", required: ["total_files", "classified"], properties: {
        total_files: { type: "number" }, classified: { type: "number" } } } } };

  const basePrompt =
    "You are Stage 1 (comprehensive understanding) of a forensic repository audit of the project at " + REPO + ".\n" +
    "The AUTHORITATIVE FILE DENOMINATOR is the JSON array of " + denom.length + " repo-relative paths at " + join(WORK, "denominator.json") + ". Read it first.\n" +
    "TASK: Actually open/inspect the repository with Read/Grep/Glob/Bash. Then:\n" +
    " 1) Classify EVERY file in the denominator: assign role (" + ROLE_ENUM.join("/") + ") and a one-line note of what it is. Your files[] MUST contain one entry per denominator path (same path strings). No role may be 'unknown' unless you truly cannot tell after reading it.\n" +
    " 2) Identify EVERY entry point — CLI commands, exported/public APIs, HTTP routes, __main__ blocks, package scripts — each with name, kind, location (path:line), and a one-line description.\n" +
    " 3) Write an architecture summary (components, data flow, how modules connect).\n" +
    " 4) Write a PROVISIONAL intent statement (the apparent reason the project exists) and explicitly label it provisional. This becomes the yardstick Stage 2 judges defects against.\n" +
    "Set coverage.total_files to the denominator count and coverage.classified to how many you classified. Obey the global invariants.";

  let r = await agentValidated({ name: "s1-map", prompt: basePrompt, schema, model: M.fast, maxTurns: 70, timeoutMs: 12e5 });
  if (!r.ok) await halt("stage1", "mapping agent could not produce a schema-valid inventory: " + r.err);

  // Coverage stop-test (computed in JS, not trusted from the agent): every denom path classified.
  let classified = new Map(r.data.files.map((f) => [f.path, f]));
  let missing = denom.filter((p) => !classified.has(p));
  for (let pass = 1; pass <= 2 && missing.length; pass++) {
    log("  coverage gap: " + missing.length + " unclassified -> augmentation pass " + pass);
    const fillSchema = { type: "object", required: ["files"], properties: { files: { type: "array", minItems: 1,
      items: { type: "object", required: ["path", "role", "note"], properties: { path: { type: "string" }, role: { type: "string", enum: ROLE_ENUM }, note: { type: "string" } } } } } };
    const fr = await agentValidated({ name: "s1-cov" + pass, model: M.fast, maxTurns: 40, timeoutMs: 6e5, schema: fillSchema,
      prompt: "Stage 1 coverage fill. Classify ONLY these repo-relative files (Read each before classifying): " + j(missing) +
        "\nFor each, give path (verbatim from this list), role (" + ROLE_ENUM.join("/") + "), and a one-line note." });
    if (fr.ok) for (const f of fr.data.files) if (!classified.has(f.path)) { classified.set(f.path, f); r.data.files.push(f); }
    missing = denom.filter((p) => !classified.has(p));
  }
  if (missing.length) await halt("stage1", "coverage not closed: " + missing.length + " files never classified: " + j(missing.slice(0, 20)));

  const unknowns = r.data.files.filter((f) => f.role === "unknown");
  // visitation evidence (best-effort): denom paths that literally appeared in tool activity
  const seen = denom.filter((p) => r.toolPaths.some((tp) => tp.endsWith(p)) || r.toolText.includes(p));
  r.data.coverage = { total_files: denom.length, classified: classified.size, visited_evidenced: seen.length, unknown: unknowns.length };
  log("  classified " + classified.size + "/" + denom.length + ", visitation-evidenced " + seen.length + ", unknown " + unknowns.length);

  const md = renderStage1(r.data, denom);
  await checkpoint("stage1", "01-understanding.md", md, "stage1.json", r.data);
  return r.data;
}

function mdTable(headers, rows) {
  const esc = (x) => String(x == null ? "" : x).replace(/\|/g, "\\|").replace(/\n/g, " ");
  return "| " + headers.join(" | ") + " |\n| " + headers.map(() => "---").join(" | ") + " |\n" +
    rows.map((r) => "| " + r.map(esc).join(" | ") + " |").join("\n");
}
function jsonDetails(obj) { return "\n\n<details><summary>machine-readable JSON (source of truth)</summary>\n\n" + "```json\n" + jp(obj) + "\n```\n</details>\n"; }

function renderStage1(d, denom) {
  const byRole = {};
  for (const f of d.files) (byRole[f.role] ||= []).push(f);
  let s = "# 01 — Comprehensive Understanding\n\n_Stage 1 of the forensic audit. Coverage denominator for all later stages. Generated " + nowts() + "._\n\n";
  s += "## Provisional intent (PROVISIONAL — refined in Stage 4)\n\n> " + d.provisional_intent.replace(/\n/g, "\n> ") + "\n\n";
  s += "## Architecture\n\n" + d.architecture + "\n\n";
  s += "## Coverage\n\n- Denominator (files, excl. `audit/`): **" + denom.length + "**\n- Classified: **" + d.coverage.classified + "**\n- Visitation-evidenced via tool activity: **" + (d.coverage.visited_evidenced ?? "n/a") + "**\n- Unknown role: **" + (d.coverage.unknown ?? 0) + "**\n\n";
  s += "## Entry points\n\n" + (d.entry_points.length ? mdTable(["Name", "Kind", "Location", "Description"], d.entry_points.map((e) => ["`" + e.name + "`", e.kind, "`" + e.location + "`", e.description])) : "_none identified_") + "\n\n";
  s += "## File inventory by role\n\n";
  for (const role of ROLE_ENUM) { const fs2 = byRole[role]; if (!fs2 || !fs2.length) continue;
    s += "### " + role + " (" + fs2.length + ")\n\n" + mdTable(["Path", "Note"], fs2.map((f) => ["`" + f.path + "`", f.note])) + "\n\n"; }
  s += jsonDetails(d);
  return s;
}

// ════════════════════════════════ STAGE 2 ════════════════════════════════
function fingerprint(f) { return (f.class + "|" + (f.location || "").toLowerCase().replace(/\s+/g, "") + "|" + (f.title || "").toLowerCase().split(/\s+/).slice(0, 6).join(" ")); }
function dedupe(findings) {
  const seen = new Map();
  for (const f of findings) { const k = fingerprint(f); if (!seen.has(k)) seen.set(k, f); }
  return [...seen.values()];
}
function reassignIds(findings) { findings.forEach((f, i) => (f.id = "F" + String(i + 1).padStart(3, "0"))); return findings; }

async function stage2(s1) {
  log("STAGE 2 — static audit");
  const surface = s1.files.filter((f) => ["source", "test", "doc", "config"].includes(f.role)).map((f) => f.path);
  const intent = s1.provisional_intent;
  const ctx = "PROVISIONAL INTENT to judge defects against:\n" + intent + "\n\nStage-1 inventory is at " + join(WORK, "stage1.json") + ". The audit surface (source/test/doc/config) is:\n" + j(surface);

  // diverse lenses, run concurrently
  const lenses = [
    { name: "s2-bugs-sec", model: M.deep, focus: "CORRECTNESS BUGS and SECURITY VULNERABILITIES: logic errors, off-by-one, wrong/with-no return values, unit/conversion errors, edge cases, concurrency/parallelism hazards, resource leaks, exception swallowing; injection, eval/exec on untrusted data, unsafe deserialization, path traversal, hardcoded secrets/paths, unsafe subprocess. Re-read the actual source — do not trust the map." },
    { name: "s2-drift-design", model: M.fast, focus: "DOCUMENTATION/CODE DRIFT, DESIGN DEFECTS, and CODE/INTENT MISMATCH: README/docstrings that disagree with code, missing or stubbed-but-documented features, dead/placeholder code, packaging/import inconsistencies, missing tests for claimed behavior, license mismatches. Any mismatch between code and the provisional intent is itself a finding (class code-intent-mismatch)." },
  ];
  let findings = [];
  const lensRes = await pMap(lenses, (L) => agentValidated({ name: L.name, model: L.model, maxTurns: 60, timeoutMs: 12e5, schema: auditFindingsSchema,
    prompt: "You are a Stage-2 static-audit lens for the repo at " + REPO + ".\n" + ctx + "\nLENS: " + L.focus +
      "\nReturn every defect you can substantiate. Each finding: short title; location as path:line; class (" + CLASS_ENUM.join("/") + "); severity (" + SEV_ENUM.join("/") + "); evidence (what in the source proves it — quote the construct, cite path:line, never paste secrets); intent_link (which intended behavior it violates). Visit the surface files directly." }), 2);
  for (const r of lensRes) if (r.ok) findings.push(...r.data.findings);
  findings = reassignIds(dedupe(findings));
  log("  initial findings: " + findings.length);
  let coverageToolText = lensRes.filter((r) => r.ok).map((r) => r.toolText).join(" ");
  let coverageToolPaths = lensRes.filter((r) => r.ok).flatMap((r) => r.toolPaths);

  // adversarial fixpoint: re-audit (add) -> falsify WHOLE set -> survivors -> stable?
  const refuted = [];
  let prevSig = "";
  const CEIL = 4;
  for (let round = 1; round <= CEIL; round++) {
    // 1) re-audit sweep for anything missed (ordering: add candidates BEFORE falsifying)
    const sweep = await agentValidated({ name: "s2-reaudit-r" + round, model: M.fast, maxTurns: 45, timeoutMs: 9e5, schema: auditFindingsSchema,
      prompt: "Stage-2 RE-AUDIT sweep (round " + round + ") for repo at " + REPO + ".\n" + ctx +
        "\nThe CURRENT finding set (titles+locations) is:\n" + j(findings.map((f) => ({ id: f.id, title: f.title, location: f.location, class: f.class }))) +
        "\nFind defects NOT already in this list — different files, different bugs, anything missed. Re-read source. Return ONLY new findings (empty array if none). Same finding shape." });
    if (sweep.ok && sweep.data.findings.length) { findings = reassignIds(dedupe([...findings, ...sweep.data.findings])); log("  round " + round + " re-audit added candidates -> " + findings.length); }
    if (sweep.ok) { coverageToolText += " " + sweep.toolText; coverageToolPaths.push(...sweep.toolPaths); }

    // 2) falsify the ENTIRE current set (adversarial promotion gate)
    const falsifySchema = { type: "object", required: ["verdicts"], properties: {
      verdicts: { type: "array", items: { type: "object", required: ["id", "verdict", "reason"], properties: {
        id: { type: "string" }, verdict: { type: "string", enum: ["upheld", "refuted", "needs-evidence"] }, reason: { type: "string" } } } } } };
    const fal = await agentValidated({ name: "s2-falsify-r" + round, model: M.deep, maxTurns: 55, timeoutMs: 12e5, schema: falsifySchema,
      prompt: "You are an ADVERSARIAL FALSIFIER for Stage 2 of the audit of " + REPO + ". You are handed CLAIMS and the SOURCE. Try to REFUTE each finding by checking it against the actual code — do not defer to the prior agent.\n" + ctx +
        "\nFINDINGS:\n" + j(findings.map((f) => ({ id: f.id, title: f.title, location: f.location, class: f.class, severity: f.severity, evidence: f.evidence }))) +
        "\nFor EACH id return verdict: 'upheld' (you independently confirmed it at the cited location), 'refuted' (the code disproves it — say why with path:line), or 'needs-evidence' (claim not substantiated at the cited anchor). Open the cited files." });
    if (!fal.ok) await halt("stage2", "falsifier failed to return verdicts in round " + round + ": " + fal.err);
    const verdict = new Map(fal.data.verdicts.map((v) => [v.id, v]));
    const survivors = [];
    for (const f of findings) { const v = verdict.get(f.id);
      if (v && v.verdict === "upheld") { f.status = "survived"; f.falsifier_note = v.reason; survivors.push(f); }
      else { f.status = v ? (v.verdict === "refuted" ? "refuted" : "unverified") : "unverified"; f.falsifier_note = v ? v.reason : "no verdict returned"; refuted.push(f); } }
    findings = reassignIds(survivors);
    coverageToolText += " " + fal.toolText; coverageToolPaths.push(...fal.toolPaths);
    log("  round " + round + " survivors after falsify: " + findings.length + " (cumulative refuted/unverified: " + refuted.length + ")");

    // 3) fixpoint test (only AFTER falsifying the latest additions)
    const sig = findings.map(fingerprint).sort().join("||");
    if (sig === prevSig) { log("  fixpoint reached at round " + round); break; }
    prevSig = sig;
    if (round === CEIL) log("  reached round ceiling; proceeding with current survivors");
  }

  // coverage stop-test: every surface item visited >=1 (evidenced from tool activity)
  const visited = new Set();
  for (const p of surface) if (coverageToolPaths.some((tp) => tp.endsWith(p)) || coverageToolText.includes(p)) visited.add(p);
  let unvisited = surface.filter((p) => !visited.has(p));
  if (unvisited.length) {
    log("  coverage: " + unvisited.length + " surface files lack visitation evidence -> targeted sweep");
    const sweep2 = await agentValidated({ name: "s2-cov-sweep", model: M.fast, maxTurns: 50, timeoutMs: 9e5, schema: auditFindingsSchema,
      prompt: "Stage-2 COVERAGE sweep. Read EACH of these files in full and report any defect (or none) per the standard finding shape: " + j(unvisited) + "\n" + ctx });
    if (sweep2.ok) { for (const p of unvisited) if (sweep2.toolPaths.some((tp) => tp.endsWith(p)) || sweep2.toolText.includes(p)) visited.add(p);
      if (sweep2.data.findings.length) { // re-falsify just the new ones before shipping
        let extra = reassignIds(sweep2.data.findings.map((f) => ({ ...f, id: "X" })));
        const fs2 = { type: "object", required: ["verdicts"], properties: { verdicts: { type: "array", items: { type: "object", required: ["id", "verdict", "reason"], properties: { id: { type: "string" }, verdict: { type: "string", enum: ["upheld", "refuted", "needs-evidence"] }, reason: { type: "string" } } } } } };
        const fe = await agentValidated({ name: "s2-falsify-cov", model: M.deep, maxTurns: 40, timeoutMs: 9e5, schema: fs2,
          prompt: "Adversarially falsify these late findings against source at " + REPO + ":\n" + j(extra.map((f) => ({ id: f.id, title: f.title, location: f.location, evidence: f.evidence }))) + "\nVerdict upheld/refuted/needs-evidence with reason + path:line." });
        if (fe.ok) { const vm = new Map(fe.data.verdicts.map((v) => [v.id, v])); for (const f of extra) { const v = vm.get(f.id); if (v && v.verdict === "upheld") { f.status = "survived"; f.falsifier_note = v.reason; findings.push(f); } else { f.status = "refuted"; f.falsifier_note = v ? v.reason : "no verdict"; refuted.push(f); } } findings = reassignIds(findings); } } }
    unvisited = surface.filter((p) => !visited.has(p));
  }

  const out = { findings, refuted_or_unverified: refuted, coverage: { surface_count: surface.length, visited: visited.size, unvisited } };
  if (unvisited.length) out.coverage.note = "Files without tool-evidenced visitation are recorded as unverified coverage, not as defect-free (invariant 1).";
  const md = renderStage2(out, intent);
  await checkpoint("stage2", "02-static-audit.md", md, "stage2.json", out);
  return out;
}

function renderStage2(d, intent) {
  const sevOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  const fs2 = [...d.findings].sort((a, b) => (sevOrder[a.severity] - sevOrder[b.severity]));
  let s = "# 02 — Static Audit\n\n_Stage 2. Defects findable by reading, each survived an independent adversarial falsification pass. Generated " + nowts() + "._\n\n";
  s += "Judged against the Stage-1 provisional intent:\n\n> " + intent.split("\n")[0] + "\n\n";
  s += "## Coverage\n\n- Audit surface (source/test/doc/config): **" + d.coverage.surface_count + "**\n- Visitation-evidenced: **" + d.coverage.visited + "**\n- Unverified (no tool evidence): **" + d.coverage.unvisited.length + "**" + (d.coverage.unvisited.length ? " — " + d.coverage.unvisited.map((p) => "`" + p + "`").join(", ") : "") + "\n\n";
  s += "## Surviving findings (" + fs2.length + ")\n\nEach below was upheld by an adversarial falsifier against the source.\n\n";
  s += fs2.length ? mdTable(["ID", "Sev", "Class", "Location", "Title"], fs2.map((f) => [f.id, f.severity, f.class, "`" + f.location + "`", f.title])) + "\n\n" : "_none survived_\n\n";
  for (const f of fs2) {
    s += "### " + f.id + " — " + f.title + "\n\n- **Severity / class:** " + f.severity + " / " + f.class + "\n- **Location:** `" + f.location + "`\n- **Evidence:** " + f.evidence + "\n- **Violates intent:** " + f.intent_link + "\n" + (f.falsifier_note ? "- **Falsifier (upheld):** " + f.falsifier_note + "\n" : "") + "\n";
  }
  if (d.refuted_or_unverified.length) {
    s += "## Refuted / unverified candidates (" + d.refuted_or_unverified.length + ")\n\nRecorded for transparency; did NOT survive falsification.\n\n" +
      mdTable(["Title", "Location", "Status", "Why"], d.refuted_or_unverified.map((f) => [f.title, "`" + f.location + "`", f.status, f.falsifier_note || ""])) + "\n\n";
  }
  s += jsonDetails(d);
  return s;
}

// ════════════════════════════════ STAGE 3 ════════════════════════════════
async function stage3(s1, s2) {
  log("STAGE 3 — execution / dynamic surface");
  const regionSchema = { type: "object", required: ["regions", "coverage_summary", "finding_deltas"], properties: {
    regions: { type: "array", minItems: 1, items: { type: "object", required: ["region", "status", "evidence"], properties: {
      region: { type: "string" }, status: { type: "string", enum: ["executed", "un-executed"] }, evidence: { type: "string" },
      blocker_class: { type: "string", enum: ["none", "requires-credentials", "external-service", "hardware-gated", "dead", "destructive-skip", "soft-blocker-unresolved"] } } } },
    coverage_summary: { type: "object", required: ["executed_count", "unexecuted_count", "accounting_complete"], properties: {
      executed_count: { type: "number" }, unexecuted_count: { type: "number" }, accounting_complete: { type: "boolean" }, measured_coverage: { type: "string" } } },
    finding_deltas: { type: "array", items: { type: "object", required: ["finding_id", "verdict", "note"], properties: {
      finding_id: { type: "string" }, verdict: { type: "string", enum: ["confirmed", "refuted", "refined", "untestable"] }, note: { type: "string" } } } } } };

  const entryList = j(s1.entry_points.map((e) => e.name + " @ " + e.location));
  const findingList = j(s2.findings.map((f) => ({ id: f.id, title: f.title, location: f.location })));
  const driver = await agentValidated({ name: "s3-execute", model: M.fast, maxTurns: 110, timeoutMs: 18e5, schema: regionSchema,
    prompt: "You are Stage 3 (dynamic execution) of the audit of " + REPO + ". This is an EPHEMERAL SANDBOX with internet and free mutation. Default posture: MAKE IT RUN.\n" +
      "Discover build/test/run commands from the repo itself (README, setup.py, requirements.txt, pytest.ini, package.json, any CI config) — never assume another project's commands.\n" +
      "You are expected to: install missing dependencies (e.g. pip install -r requirements.txt and whatever else imports need), set dummy/fake env vars, stub external services/credentialed clients at the boundary, and write THROWAWAY harnesses to drive entry points that lack tests. None of this persists.\n" +
      "Drive ACTUAL PRODUCTION CODE: import the project's modules and call their functions/classes with real inputs; capture real outputs and real errors (tracebacks). A passing test suite is NOT execution evidence on its own — tests count only insofar as they actually run production code; untested entry points (" + entryList + ") must be driven directly.\n" +
      "For EACH region (every source module from Stage 1, plus every entry point and key public function) record status:\n" +
      " - 'executed' => production code ran and you OBSERVED behavior; put the command/harness and the captured input->output or traceback in evidence.\n" +
      " - 'un-executed' => allowed ONLY with proof-of-attempt in evidence: the exact command you ran, the actual failure output, and for soft blockers the stub/fake you tried and why real logic still couldn't be reached. Set blocker_class. 'needs dependencies'/'needs credentials' are presumptively defeatable (install/stub) and may be claimed only after a shown failed attempt; genuine blockers are narrow (hardware absent w/ failing probe, destructive beyond sandbox isolation, or provably dead code).\n" +
      "Then use what you observed to confirm/refute/refine the Stage-2 findings (finding_deltas), especially numeric/bug claims: " + findingList + "\n" +
      "Set coverage_summary.accounting_complete true only if every region is executed OR un-executed-with-proof. Report measured_coverage if you obtained a coverage number. Obey invariants (cite locations; never paste secrets)." });
  if (!driver.ok) await halt("stage3", "execution agent could not produce a schema-valid execution object: " + driver.err);
  let regions = driver.data.regions;

  // adversarial accounting pass: independently try to RUN everything marked un-executed
  const unexec = regions.filter((r) => r.status === "un-executed");
  let flipped = [];
  if (unexec.length) {
    const acc = await agentValidated({ name: "s3-accounting", model: M.fast, maxTurns: 90, timeoutMs: 15e5, schema: regionSchema,
      prompt: "You are the Stage-3 ADVERSARIAL ACCOUNTING pass for " + REPO + ". A prior agent marked these regions un-executed:\n" +
        j(unexec.map((r) => ({ region: r.region, evidence: r.evidence, blocker_class: r.blocker_class }))) +
        "\nYour job: try to RUN each of them anyway — install deps, set fake env vars, stub external/credentialed boundaries, write throwaway harnesses that import and call the real code. Whatever you get running flips to 'executed' (put the harness + observed output in evidence); the original classification was false. Only keep 'un-executed' with hardened proof-of-attempt (command + failure + stub tried). Return the FULL updated region list for these regions plus a finding_deltas array (may be empty) and a coverage_summary." });
    if (acc.ok) {
      const accMap = new Map(acc.data.regions.map((r) => [r.region, r]));
      regions = regions.map((r) => { const a = accMap.get(r.region); if (a && r.status === "un-executed" && a.status === "executed") { flipped.push(r.region); return a; } return a && r.status === "un-executed" ? a : r; });
      driver.data.finding_deltas.push(...(acc.data.finding_deltas || []));
    }
  }
  if (flipped.length) log("  accounting flipped to executed: " + flipped.length + " region(s)");

  // independent orchestrator-side ground truth: try the repo's own test path, capture the real result
  let orchProbe = { attempted: false };
  const hasReq = existsSync(join(REPO, "requirements.txt"));
  if (hasReq) await sh("bash", ["-lc", "pip install -q -r requirements.txt >/dev/null 2>&1 || true"]);
  await sh("bash", ["-lc", "pip install -q pytest numpy scipy >/dev/null 2>&1 || true"]);
  const pt = await sh("bash", ["-lc", "python3 -m pytest -q 2>&1 | tail -25"]);
  orchProbe = { attempted: true, command: "python3 -m pytest -q", tail: pt.out.trim().slice(-1500) };
  log("  orchestrator test probe: " + (orchProbe.tail.split("\n").slice(-1)[0] || "(no output)"));

  const exec = regions.filter((r) => r.status === "executed").length;
  const un = regions.length - exec;
  const accounting_complete = regions.every((r) => r.status === "executed" || (r.evidence && r.evidence.length > 30));
  const out = { regions, coverage_summary: { executed_count: exec, unexecuted_count: un, accounting_complete, measured_coverage: driver.data.coverage_summary?.measured_coverage || "not-measured", flipped_by_accounting: flipped },
    finding_deltas: driver.data.finding_deltas, orchestrator_probe: orchProbe };
  if (!accounting_complete) log("  WARNING: some un-executed regions lack proof-of-attempt; recorded as unverified accounting");
  const md = renderStage3(out);
  await checkpoint("stage3", "03-execution.md", md, "stage3.json", out);
  return out;
}

function renderStage3(d) {
  let s = "# 03 — Execution / Dynamic Surface\n\n_Stage 3. What the code actually does when run. 100% accounting: every region executed, or un-executed with proof-of-attempt. Generated " + nowts() + "._\n\n";
  s += "## Summary\n\n- Regions executed: **" + d.coverage_summary.executed_count + "**\n- Regions un-executed (with proof): **" + d.coverage_summary.unexecuted_count + "**\n- Accounting complete: **" + d.coverage_summary.accounting_complete + "**\n- Measured coverage: **" + d.coverage_summary.measured_coverage + "**\n- Flipped to executed by adversarial accounting: **" + (d.coverage_summary.flipped_by_accounting || []).length + "**\n\n";
  s += "### Orchestrator-side independent probe\n\n`" + d.orchestrator_probe.command + "`\n\n```\n" + (d.orchestrator_probe.tail || "(not attempted)") + "\n```\n\n";
  s += "## Regions\n\n" + mdTable(["Region", "Status", "Blocker", "Evidence"], d.regions.map((r) => [r.region, r.status, r.blocker_class || "", (r.evidence || "").slice(0, 240)])) + "\n\n";
  if (d.finding_deltas.length) s += "## Effect on Stage-2 findings\n\n" + mdTable(["Finding", "Verdict", "Note"], d.finding_deltas.map((x) => [x.finding_id, x.verdict, x.note])) + "\n\n";
  s += jsonDetails(d);
  return s;
}

// ════════════════════════════════ STAGE 4 ════════════════════════════════
async function stage4(s1, s2, s3) {
  log("STAGE 4 — goal + external research (parallel)");
  const goalSchema = { type: "object", required: ["candidate_goals"], properties: { candidate_goals: { type: "array", minItems: 1, items: { type: "object",
    required: ["goal", "success_signals", "grounding", "confidence"], properties: { goal: { type: "string" },
      success_signals: { type: "array", minItems: 1, items: { type: "string" } },
      grounding: { type: "array", minItems: 1, items: { type: "string" } },
      confidence: { type: "string", enum: ["grounded", "needs-human-confirmation"] } } } } } };
  const researchSchema = { type: "object", required: ["items"], properties: { items: { type: "array", items: { type: "object",
    required: ["idea", "relevance", "sources", "corroboration"], properties: { idea: { type: "string" }, relevance: { type: "string" },
      sources: { type: "array", minItems: 1, items: { type: "object", required: ["title", "url"], properties: { title: { type: "string" }, url: { type: "string" } } } },
      corroboration: { type: "string", enum: ["corroborated", "single-source", "unverified"] } } } }, saturation: { type: "string" } } };

  const sharedCtx = "Stage-1 inventory: " + join(WORK, "stage1.json") + "; Stage-2 findings: " + join(WORK, "stage2.json") + "; Stage-3 execution: " + join(WORK, "stage3.json") + ". Provisional intent: " + s1.provisional_intent;

  const goalP = agentValidated({ name: "s4-goal", model: M.deep, maxTurns: 45, timeoutMs: 9e5, schema: goalSchema,
    prompt: "Stage 4 GOAL half for " + REPO + ". Infer the repo's candidate LONG-TERM goal(s). " + sharedCtx +
      "\nState each candidate as a goal plus a set of FALSIFIABLE success_signals (observable conditions that would show the goal is met). EVERY signal and the goal itself must be grounded: each grounding entry cites a concrete Stage 1-3 artifact (a path:line, a finding id, an entry point, or an observed behavior). A candidate with no grounding is speculation — drop it or mark confidence 'needs-human-confirmation'. Keep candidates PLURAL; do not collapse to one. Read the prior-stage JSON before answering." });

  // research half — deep-research shape: independent gatherers, then a weigher
  const seed = "Domain seed (from Stage 1): " + s1.provisional_intent + "\nArchitecture: " + (s1.architecture || "").slice(0, 600);
  const gather = async (angle, idx) => agentValidated({ name: "s4-research-" + idx, model: M.web, web: true, maxTurns: 30, timeoutMs: 12e5, schema: researchSchema,
    prompt: "Stage 4 RESEARCH gather (angle: " + angle + ") for the project at " + REPO + ". " + seed +
      "\nSearch the web for ideas, technologies, libraries, papers, and projects that would MATERIALLY ADVANCE this project's apparent goal. Focus on the " + angle + " angle. For each item: the idea, its relevance to the goal, >=1 source (title+url), and a corroboration tag. Cite every source; an uncorroborated claim is 'unverified', not fact. Aim for high-signal, specific, real sources." });
  const angles = ["domain methods & primary literature (the scientific approach this code implements)", "engineering: libraries/tools/frameworks that strengthen the implementation and its testing/validation"];

  const [goalR, gA, gB] = await Promise.all([goalP, gather(angles[0], 1), gather(angles[1], 2)]);

  let research = { items: [], saturation: "" };
  const gathered = [gA, gB].filter((r) => r.ok).flatMap((r) => r.data.items);
  if (gathered.length) {
    const weigh = await agentValidated({ name: "s4-research-weigh", model: M.fast, web: true, maxTurns: 25, timeoutMs: 9e5, schema: researchSchema,
      prompt: "Stage 4 RESEARCH weigher. Independent gatherers returned these items for the project at " + REPO + ":\n" + j(gathered) +
        "\nCross-check their sources against each other and (briefly) the web. Merge duplicates, drop the unsupportable, downgrade single-source claims, and KEEP the corroboration honest (corroborated only if >=2 independent reputable sources agree). Return the consolidated item list and a one-line saturation note (are returns diminishing?). Keep every kept item's sources." });
    research = weigh.ok ? weigh.data : { items: gathered, saturation: "weigher failed; raw union retained" };
  } else research = { items: [], saturation: "no research items gathered (web may be constrained); recorded as unverified, not absent" };

  if (!goalR.ok) await halt("stage4", "goal agent could not produce grounded candidate goals: " + goalR.err);
  const out = { candidate_goals: goalR.data.candidate_goals, research };
  const md = renderStage4(out);
  await checkpoint("stage4", "04-goal.md", md, "stage4.json", out);
  return out;
}

function renderStage4(d) {
  let s = "# 04 — Goal + External Research\n\n_Stage 4. The repo's grounded long-term goal(s) and external ideas that serve them. Generated " + nowts() + "._\n\n";
  s += "## Candidate long-term goals (kept plural by design)\n\n";
  d.candidate_goals.forEach((g, i) => {
    s += "### Goal " + (i + 1) + " (" + g.confidence + ")\n\n" + g.goal + "\n\n**Falsifiable success signals:**\n" + g.success_signals.map((x) => "- " + x).join("\n") + "\n\n**Grounding (Stage 1-3 evidence):**\n" + g.grounding.map((x) => "- " + x).join("\n") + "\n\n";
  });
  s += "## External research\n\n_" + (d.research.saturation || "") + "_\n\n";
  if (d.research.items.length) for (const it of d.research.items) {
    s += "### " + it.idea + " (" + it.corroboration + ")\n\n- **Relevance:** " + it.relevance + "\n- **Sources:** " + it.sources.map((x) => "[" + x.title + "](" + x.url + ")").join("; ") + "\n\n";
  } else s += "_No corroborated external items recorded._\n\n";
  s += jsonDetails(d);
  return s;
}

// ════════════════════════════════ STAGE 5 ════════════════════════════════
async function stage5(s1, s2, s3, s4) {
  log("STAGE 5 — execution-ready plan");
  const planSchema = { type: "object", required: ["items"], properties: { items: { type: "array", minItems: 1, items: { type: "object",
    required: ["id", "title", "links_to", "location", "change", "verification_signal", "depends_on", "priority"], properties: {
      id: { type: "string" }, title: { type: "string" },
      links_to: { type: "array", minItems: 1, items: { type: "string" } }, location: { type: "string" },
      change: { type: "string" }, verification_signal: { type: "string" },
      depends_on: { type: "array", items: { type: "string" } }, priority: { type: "string", enum: ["P0", "P1", "P2", "P3"] } } } } } };

  const ctx = "Inputs (read them): Stage1 " + join(WORK, "stage1.json") + ", Stage2 " + join(WORK, "stage2.json") + ", Stage3 " + join(WORK, "stage3.json") + ", Stage4 " + join(WORK, "stage4.json") +
    ".\nSurviving findings: " + j(s2.findings.map((f) => ({ id: f.id, title: f.title, location: f.location, severity: f.severity }))) +
    "\nCandidate goals: " + j(s4.candidate_goals.map((g) => g.goal));

  let plan = null, lastFeedback = "";
  for (let round = 1; round <= 2; round++) {
    const r = await agentValidated({ name: "s5-plan-r" + round, model: M.deep, maxTurns: 50, timeoutMs: 12e5, schema: planSchema,
      prompt: "Stage 5: produce the EXECUTION-READY change plan that closes the gap between current state (Stages 1-3) and goal (Stage 4) for " + REPO + ".\n" + ctx +
        "\nProduce ordered change items. EACH item MUST have: id; title; links_to (>=1 Stage-2 finding id OR a Stage-4 goal-gap it serves); location (the file/module to change); change (concretely what to do); verification_signal (the exact observation or test that proves it worked); depends_on (ids of items that must precede it); priority (P0 worst-first). Order by dependency then severity. A fresh engineer must be able to map every step to a concrete diff WITHOUT asking a clarifying question." +
        (round > 1 ? "\n\nThe previous plan had UNRESOLVABLE/ambiguous items; fix exactly these: " + lastFeedback : "") });
    if (!r.ok) { if (round === 2) await halt("stage5", "plan agent failed to produce a schema-valid plan: " + r.err); continue; }
    plan = r.data;

    // convergence gate: a FRESH agent checks each item maps to a concrete diff with no clarifying question
    const convSchema = { type: "object", required: ["items", "all_resolvable"], properties: { items: { type: "array", items: { type: "object",
      required: ["id", "resolvable"], properties: { id: { type: "string" }, resolvable: { type: "boolean" }, missing: { type: "string" } } } }, all_resolvable: { type: "boolean" } } };
    const conv = await agentValidated({ name: "s5-converge-r" + round, model: M.fast, maxTurns: 35, timeoutMs: 9e5, schema: convSchema,
      prompt: "You are a FRESH engineer handed this change plan for " + REPO + " plus the repo. For EACH item decide: can you map it to a concrete diff target (specific file + specific edit) and start work WITHOUT asking a clarifying question? Open the cited locations to check they exist.\nPLAN:\n" + j(plan.items) + "\nReturn per-item resolvable true/false (+ what's missing if false) and all_resolvable." });
    if (conv.ok && conv.data.all_resolvable) { log("  plan converged at round " + round); break; }
    lastFeedback = conv.ok ? j(conv.data.items.filter((x) => !x.resolvable)) : "convergence check failed to run";
    log("  plan round " + round + " not fully resolvable: " + lastFeedback.slice(0, 200));
  }
  // completeness check (in JS): every item has all required links/signal/location/dependency
  const incomplete = plan.items.filter((it) => !it.links_to?.length || !it.verification_signal || !it.location || it.depends_on == null);
  if (incomplete.length) await halt("stage5", "plan items missing required fields: " + j(incomplete.map((i) => i.id)));

  const md = renderStage5(plan);
  await checkpoint("stage5", "05-plan.md", md, "stage5.json", plan);
  return plan;
}

function renderStage5(d) {
  const pr = { P0: 0, P1: 1, P2: 2, P3: 3 };
  const items = [...d.items].sort((a, b) => pr[a.priority] - pr[b.priority]);
  let s = "# 05 — Execution-Ready Plan\n\n_Stage 5. Ordered, dependency-aware change items closing the gap to the Stage-4 goal. Every item links to a finding/goal, names a location, and carries a verification signal. Generated " + nowts() + "._\n\n";
  s += mdTable(["ID", "Pri", "Title", "Links", "Location", "Depends on"], items.map((i) => [i.id, i.priority, i.title, i.links_to.join(", "), "`" + i.location + "`", (i.depends_on || []).join(", ") || "—"])) + "\n\n";
  for (const i of items) {
    s += "### " + i.id + " [" + i.priority + "] — " + i.title + "\n\n- **Closes:** " + i.links_to.join(", ") + "\n- **Location:** `" + i.location + "`\n- **Change:** " + i.change + "\n- **Verification signal:** " + i.verification_signal + "\n- **Depends on:** " + ((i.depends_on || []).join(", ") || "nothing") + "\n\n";
  }
  s += jsonDetails(d);
  return s;
}

// ───────────────────────────── preflight (auth + tool-use + file handoff) ─────────────────────────────
async function preflight() {
  log("PREFLIGHT — proving auth + Bash + Write file-handoff under acceptEdits (root)");
  const schema = { type: "object", required: ["ok", "repo_first_path", "bash_echo"], properties: {
    ok: { type: "boolean" }, repo_first_path: { type: "string" }, bash_echo: { type: "string" } } };
  const r = await agentValidated({ name: "preflight", model: M.fast, maxTurns: 8, timeoutMs: 18e4, schema,
    prompt: "Preflight check. Do exactly three things: (1) use Bash to run `git ls-files | head -1` in " + REPO + " and capture the line; (2) use Read to open that file; (3) report. Put the first repo path in repo_first_path, the bash output in bash_echo, and ok=true." });
  if (r.ok) { log("PREFLIGHT PASS — first path: " + r.data.repo_first_path); return true; }
  log("PREFLIGHT FAIL — " + r.err); return false;
}

// ───────────────────────────── main ─────────────────────────────
async function main() {
  mkdirSync(WORK, { recursive: true });
  BRANCH = (await sh("git", ["rev-parse", "--abbrev-ref", "HEAD"])).out.trim() || "HEAD";
  log("repo=" + REPO + " branch=" + BRANCH);

  if (FLAG("--fresh")) { log("--fresh: tearing down prior audit outputs");
    for (const f of ["01-understanding.md", "02-static-audit.md", "03-execution.md", "04-goal.md", "05-plan.md", "HALT-REPORT.md"]) try { rmSync(join(AUDIT, f)); } catch {}
    try { rmSync(WORK, { recursive: true, force: true }); } catch {} mkdirSync(WORK, { recursive: true }); }

  if (FLAG("--preflight")) { const ok = await preflight(); process.exit(ok ? 0 : 1); }

  if (!FLAG("--no-preflight")) { const ok = await preflight(); if (!ok) await halt("preflight", "claude -p could not prove auth + tool-use + file handoff; aborting before the long run."); }

  const st = readState();
  const done = (k) => !!st.completed[k] && existsSync(join(WORK, k + ".json"));
  const load = (k) => loadJson(join(WORK, k + ".json"));
  const only = ARGVAL("--stage");

  let s1, s2, s3, s4;
  const want = (n) => !only || only === String(n);

  if (want(1)) s1 = done("stage1") && !FLAG("--fresh") ? (log("resume: stage1 done"), load("stage1")) : await stage1();
  else s1 = load("stage1");
  if (want(2)) s2 = done("stage2") && !only ? (log("resume: stage2 done"), load("stage2")) : await stage2(s1);
  else s2 = load("stage2");
  if (want(3)) s3 = done("stage3") && !only ? (log("resume: stage3 done"), load("stage3")) : await stage3(s1, s2);
  else s3 = load("stage3");
  if (want(4)) s4 = done("stage4") && !only ? (log("resume: stage4 done"), load("stage4")) : await stage4(s1, s2, s3);
  else s4 = load("stage4");
  if (want(5)) { if (done("stage5") && !only) log("resume: stage5 done"); else await stage5(s1, s2, s3, s4); }

  log("PIPELINE COMPLETE. API-equivalent cost (NOT real subscription spend): $" + TOTAL_COST.toFixed(2));
  log("Artifacts: audit/01-understanding.md .. audit/05-plan.md");
}
main().catch((e) => { log("FATAL " + (e && e.stack ? e.stack : e)); process.exit(1); });
