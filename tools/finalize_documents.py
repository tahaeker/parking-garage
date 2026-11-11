"""Insert captured logs and index actual screenshots in the Markdown deliverables."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
report = ROOT / "autopsy_report.md"
content = report.read_text(encoding="utf-8")
heading = "## 9. Final test output"
end_heading = "## 10. Limits and submission status"
before = content.split(heading, 1)[0]
after = content.split(end_heading, 1)[1]
log = (ROOT / "trace_evidence/logs/03-final-tests.txt").read_text(encoding="utf-8")
section = (heading + "\n\nThe following output was captured by running Maven against the final sources. "
           "The supplied suite passes **6/7** because of the Truck assertion discussed above. The failure is preserved.\n\n"
           + "```text\n" + log.rstrip() + "\n```\n\n")
report.write_text(before + section + end_heading + after, encoding="utf-8", newline="\n")

descriptions = {
    "motorcycle-current.png": (
        "Current Motorcycle — null check",
        "Paused at src/main/java/garage/Motorcycle.java:18. "
        "The variables show spot = null, licensePlate = MOTO-002, and an initialized enteredAt. "
        "This capture uses the corrected source."),
    "motorcycle-reproduction.png": (
        "Motorcycle — reproduction of the old failure",
        "The source shown is Motorcycle.java:19 under trace_evidence/snapshots/reproduce-motorcycle-failure. "
        "The old code calls getWidth while spot is null. "
        "This session is separate from the corrected-source session. "
        "The reproduction source was opened manually while paused at the method breakpoint with the fitsInSpot:19 frame selected; "
        "the Variables panel contains values from the running old version."),
    "truck-current.png": (
        "Truck — initialized entry time",
        "IDE debugger capture showing a non-null entry time in the current Truck test."),
}
images = sorted((ROOT / "trace_evidence/screenshots").glob("*.png"))
index = []
metadata = []
for path in images:
    if path.name not in descriptions:
        raise ValueError(f"Screenshot needs a verified description: {path.name}")
    title, description = descriptions[path.name]
    index.append(f"### {title}\n\n{description}\n\n![{title}](screenshots/{path.name})\n")
    metadata.append({"file": path.name, "description": description,
                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
evidence_readme = ROOT / "trace_evidence/README.md"
readme = evidence_readme.read_text(encoding="utf-8")
marker = "<!-- SCREENSHOT_INDEX -->"
if marker in readme:
    readme = readme.replace(marker, "\n".join(index))
else:
    readme = readme.split("### ", 1)[0] + "\n".join(index)
evidence_readme.write_text(readme, encoding="utf-8", newline="\n")
(ROOT / "trace_evidence/screenshots/manifest.json").write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

checklist = ROOT / "SUBMISSION.md"
text = checklist.read_text(encoding="utf-8")
line = "- [x] Three debugger transcripts recorded."
if "Two IDE screenshots saved" not in text and images:
    text = text.replace(line, line + "\n- [x] Two IDE screenshots saved; two forms of trace evidence are available.")
checklist.write_text(text, encoding="utf-8", newline="\n")

documents = [ROOT / name for name in ["README.md", "SUBMISSION.md", "autopsy_report.md", "reflection.md", "ai_log.md"]]
documents += [ROOT / "docs/viva_notes.md", evidence_readme]
errors = []
for path in documents:
    text = path.read_text(encoding="utf-8")
    path.write_text(text, encoding="utf-8", newline="\n")
    if sum(line.startswith("```") for line in text.splitlines()) % 2:
        errors.append(f"Unclosed code fence: {path.name}")
    if "<!--" in text:
        errors.append(f"Unfilled marker: {path.name}")
    without_code = re.sub(r"```.*?```", "", text, flags=re.S)
    for target in re.findall(r"\]\(([^)]+)\)", without_code):
        if "://" not in target and not target.startswith("#"):
            if not (path.parent / target.split("#", 1)[0]).exists():
                errors.append(f"Missing link: {path.name} -> {target}")
reflection_words = len((ROOT / "reflection.md").read_text(encoding="utf-8").split())
if reflection_words > 250:
    errors.append(f"Reflection exceeds 250 words: {reflection_words}")
result = {"checked_documents": len(documents), "reflection_words": reflection_words,
          "debugger_screenshots": len(images), "errors": errors}
for source_name, destination_name in [("TEST-garage.GarageTest.xml", "final-junit.xml"),
                                      ("garage.GarageTest.txt", "final-junit.txt")]:
    source = ROOT / "target/surefire-reports" / source_name
    if source.is_file():
        shutil.copy2(source, ROOT / "trace_evidence/logs" / destination_name)
suite = ET.parse(ROOT / "trace_evidence/logs/final-junit.xml").getroot()
result["supplied_junit"] = {name: int(suite.get(name, "0")) for name in ["tests", "failures", "errors", "skipped"]}
if result["supplied_junit"] != {"tests": 7, "failures": 1, "errors": 0, "skipped": 0}:
    errors.append("The report's stated JUnit result needs updating to match the recorded XML.")
(ROOT / "trace_evidence/document_checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
if errors:
    raise SystemExit(1)
