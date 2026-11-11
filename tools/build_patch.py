"""Build and verify the source-only patch against the normalized original snapshot."""
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "trace_evidence/snapshots/repository-original"
parts = []
changed = []
for original in sorted((BASELINE / "src/main/java/garage").glob("*.java")):
    relative = original.relative_to(BASELINE).as_posix()
    current = ROOT / relative
    before = original.read_text(encoding="utf-8")
    after = current.read_text(encoding="utf-8")
    if before == after:
        continue
    changed.append(relative)
    parts.append(f"diff --git a/{relative} b/{relative}\n")
    for line in difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                     fromfile=f"a/{relative}", tofile=f"b/{relative}"):
        parts.append(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
patch = ROOT / "fix.patch"
patch.write_text("".join(parts), encoding="utf-8", newline="\n")
workspace = Path(tempfile.mkdtemp(prefix="garage-patch-check-"))
shutil.copytree(BASELINE / "src", workspace / "src")
check = subprocess.run(["git", "apply", "--check", str(patch)], cwd=workspace,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
if check.returncode:
    raise RuntimeError(check.stdout + check.stderr)
subprocess.run(["git", "apply", str(patch)], cwd=workspace, check=True,
               capture_output=True, text=True, encoding="utf-8", errors="replace")
for relative in changed:
    if (workspace / relative).read_text(encoding="utf-8") != (ROOT / relative).read_text(encoding="utf-8"):
        raise AssertionError(f"Patch mismatch: {relative}")
test = ROOT / "src/test/java/garage/GarageTest.java"
manifest = json.loads((ROOT / "trace_evidence/capture_manifest.json").read_text(encoding="utf-8"))
test_hash = hashlib.sha256(test.read_bytes()).hexdigest()
test_unchanged = test_hash == manifest["supplied_test_sha256"]
if not test_unchanged:
    raise AssertionError("The supplied test file changed during preparation")
original_test = (BASELINE / "src/test/java/garage/GarageTest.java").read_text(encoding="utf-8")
result = {
    "patch_paths": changed,
    "patch_apply_check": "passed",
    "patched_sources_match_final_sources": True,
    "supplied_test_unchanged_since_capture": test_unchanged,
    "supplied_test_matches_git_HEAD_ignoring_line_endings": test.read_text(encoding="utf-8") == original_test,
    "supplied_test_sha256": test_hash,
}
(ROOT / "trace_evidence/verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
