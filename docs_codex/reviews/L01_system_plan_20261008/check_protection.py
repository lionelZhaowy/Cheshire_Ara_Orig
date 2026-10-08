"""Read-only comparison against this planning turn's incoming file hashes."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ALLOWED = {
    "docs_codex/03-08_Topic_Readiness_2026-10-08.md",
    "docs_codex/L01_Next_Tasks_Prompts_2026-10-08.md",
    "docs_codex/PROJECT_STATE.md",
    "docs_codex/AGENT_TASKS.md",
    "docs_codex/handoffs/README.md",
}
baseline = json.loads((HERE / "input.json").read_text())
changed = []
for name, expected in baseline["files"].items():
    path = ROOT / name
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        changed.append(name)
unexpected = sorted(set(changed) - ALLOWED)
print("Baseline files:", len(baseline["files"]))
print("Unchanged input files:", len(baseline["files"]) - len(changed))
print("Changed within explicit scope:")
for name in sorted(set(changed) & ALLOWED):
    print(" ", name)
for name in unexpected:
    print("UNEXPECTED:", name)
assert not unexpected, "Incoming files changed outside planning scope"
assert "docs_codex/learning/figures/20261007/editable/diagrams.pptx" in baseline["files"]
print("PASS: incoming textbook, figures, historical evidence and other protected files unchanged")
