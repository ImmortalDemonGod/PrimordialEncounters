// recon-stage2.mjs — reconstruct the live Stage-2 survivor set from on-disk agent outputs,
// by replaying the orchestrator's EXACT deterministic aggregation. Produces a durable artifact
// WITHOUT touching the still-running process. Validated against the run log (46->45->49->49).
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
const WORK = "audit/.work";
const load = (p) => JSON.parse(readFileSync(join(WORK, p), "utf8"));
const nowts = () => new Date().toISOString();

// --- exact copies of the orchestrator's pure functions ---
function primaryAnchor(loc) { return String(loc || "").split(/[,;]/)[0].trim().toLowerCase().replace(/\s+/g, ""); }
function fingerprint(f) { return f.class + "|" + primaryAnchor(f.location) + "|" + (f.title || "").toLowerCase().split(/\s+/).slice(0, 5).join(" "); }
function dedupe(findings) { const seen = new Map(); for (const f of findings) { const k = fingerprint(f); if (!seen.has(k)) seen.set(k, f); } return [...seen.values()]; }
function reassignIds(findings) { findings.forEach((f, i) => (f.id = "F" + String(i + 1).padStart(3, "0"))); return findings; }

const refutedAll = [];
function applyFalsify(findings, batchFiles) {
  const verdicts = new Map();
  for (const bf of batchFiles) if (existsSync(join(WORK, bf))) for (const v of load(bf).verdicts) verdicts.set(v.id, v);
  const survivors = [];
  for (const f of findings) { const v = verdicts.get(f.id);
    if (v && v.verdict === "upheld") { f.status = "survived"; f.falsifier_note = v.reason; survivors.push(f); }
    else { f.status = v ? (v.verdict === "refuted" ? "refuted" : "unverified") : "unverified"; f.falsifier_note = v ? v.reason : "no verdict (batch missing)"; refutedAll.push(f); } }
  return reassignIds(survivors);
}

// === replay (file selection mirrors this run's SEQ/retry pattern) ===
const bugs = load("a_s2_bugs_sec_retry_2.json").findings;   // attempt-1 failed validation -> retry used
const drift = load("a_s2_drift_design_1.json").findings;
let findings = reassignIds(dedupe([...bugs, ...drift]));
const trace = [["after lenses+dedupe", findings.length]];

const r1re = load("a_s2_reaudit_r1_3.json").findings;
if (r1re.length) findings = reassignIds(dedupe([...findings, ...r1re]));
trace.push(["after r1 re-audit (log:46)", findings.length]);
findings = applyFalsify(findings, ["a_s2_falsify_r1_b0_4.json","a_s2_falsify_r1_b1_5.json","a_s2_falsify_r1_b2_6.json","a_s2_falsify_r1_b3_7.json","a_s2_falsify_r1_b4_8.json","a_s2_falsify_r1_b5_9.json"]);
trace.push(["after r1 falsify (log:45)", findings.length]);

const r2re = load("a_s2_reaudit_r2_10.json").findings;
if (r2re.length) findings = reassignIds(dedupe([...findings, ...r2re]));
trace.push(["after r2 re-audit (log:49)", findings.length]);
findings = applyFalsify(findings, ["a_s2_falsify_r2_b0_11.json","a_s2_falsify_r2_b1_12.json","a_s2_falsify_r2_b2_13.json","a_s2_falsify_r2_b3_14.json","a_s2_falsify_r2_b4_15.json","a_s2_falsify_r2_b5_16.json","a_s2_falsify_r2_b6_17.json"]);
trace.push(["after r2 falsify (log:49)", findings.length]);

console.log("=== reconstruction trace (compare to run log) ===");
for (const [k, v] of trace) console.log("  " + k + ": " + v);

const out = { findings, refuted_or_unverified: refutedAll,
  coverage: { surface_count: null, visited: null, note: "reconstructed mid-run; coverage finalized at the live checkpoint" },
  _reconstruction: { at: nowts(), source: "audit/.work/a_s2_*.json (this run)", reflects: "round-2 survivor set", caveat: "the live process is finishing round 3; the official 02-static-audit.md will supersede this if it checkpoints" } };
writeFileSync(join(WORK, "stage2.reconstructed.json"), JSON.stringify(out, null, 2));

// --- render markdown (mirrors orchestrator renderStage2) ---
const esc = (x) => String(x == null ? "" : x).replace(/\|/g, "\\|").replace(/\n/g, " ");
const mdTable = (h, rows) => "| " + h.join(" | ") + " |\n| " + h.map(() => "---").join(" | ") + " |\n" + rows.map((r) => "| " + r.map(esc).join(" | ") + " |").join("\n");
const sevOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
const fs2 = [...findings].sort((a, b) => sevOrder[a.severity] - sevOrder[b.severity]);
let s = "# 02 — Static Audit (RECONSTRUCTED mid-run)\n\n";
s += "> **Durable snapshot reconstructed from on-disk agent outputs at " + nowts() + "**, by replaying the orchestrator's deterministic aggregation. Reflects the **round-2 survivor set** (the last completed adversarial round). The live process is finishing round 3; if it checkpoints, the official `02-static-audit.md` supersedes this file. Counts validated against the run log (46→45→49→49).\n\n";
s += "## Surviving findings (" + fs2.length + ") — each upheld by an independent batched falsifier\n\n";
s += mdTable(["ID", "Sev", "Class", "Location", "Title"], fs2.map((f) => [f.id, f.severity, f.class, "`" + f.location + "`", f.title])) + "\n\n";
for (const f of fs2) s += "### " + f.id + " — " + f.title + "\n\n- **Severity / class:** " + f.severity + " / " + f.class + "\n- **Location:** `" + f.location + "`\n- **Evidence:** " + f.evidence + "\n- **Violates intent:** " + (f.intent_link || "") + "\n" + (f.falsifier_note ? "- **Falsifier (upheld):** " + f.falsifier_note + "\n" : "") + "\n";
if (refutedAll.length) s += "## Refuted / unverified candidates (" + refutedAll.length + ")\n\n" + mdTable(["Title", "Location", "Status", "Why"], refutedAll.map((f) => [f.title, "`" + f.location + "`", f.status, f.falsifier_note || ""])) + "\n\n";
s += "\n<details><summary>machine-readable JSON</summary>\n\n```json\n" + JSON.stringify(out, null, 2) + "\n```\n</details>\n";
writeFileSync("audit/02-static-audit.RECONSTRUCTED.md", s);
console.log("\nwrote audit/02-static-audit.RECONSTRUCTED.md (" + fs2.length + " survivors, " + refutedAll.length + " refuted/unverified)");
