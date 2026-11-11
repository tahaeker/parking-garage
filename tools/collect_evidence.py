"""Collect real compiler/test/debugger evidence without changing the supplied tests."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "trace_evidence"
SOURCE_NAMES = ["Car", "Garage", "Motorcycle", "Spot", "Truck", "Vehicle"]
UTF8 = dict(encoding="utf-8", errors="replace")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def run_record(command: list[str], path: Path, cwd: Path = ROOT) -> int:
    result = subprocess.run(command, cwd=cwd, capture_output=True, **UTF8)
    header = (f"Captured: {dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat()}\n"
              f"Working directory: {cwd}\nCommand: {subprocess.list2cmdline(command)}\n"
              f"Exit code: {result.returncode}\n\n")
    write(path, header + result.stdout + result.stderr)
    print(f"{path.relative_to(ROOT)}: exit={result.returncode}")
    return result.returncode


def maven() -> str:
    found = shutil.which("mvn.cmd") or shutil.which("mvn")
    fallback = Path.home() / "AppData/Local/Programs/ApacheMaven/apache-maven-3.9.16/bin/mvn.cmd"
    if found:
        return found
    if fallback.is_file():
        return str(fallback)
    raise FileNotFoundError("Maven was not found; add its bin directory to PATH.")


def junit_classpath() -> str:
    repository = Path.home() / ".m2/repository"
    jars = [
        "org/junit/jupiter/junit-jupiter-api/5.10.2/junit-jupiter-api-5.10.2.jar",
        "org/junit/platform/junit-platform-commons/1.10.2/junit-platform-commons-1.10.2.jar",
        "org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar",
        "org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar",
    ]
    paths = [repository / jar for jar in jars]
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Run mvn test first. Missing dependency: {path}")
    return os.pathsep.join(map(str, paths))


def prepare() -> None:
    snapshot = EVIDENCE / "snapshots/repository-original"
    if snapshot.exists():
        raise FileExistsError("Original snapshot already exists; refusing to overwrite it.")
    for name in SOURCE_NAMES:
        git_name = "vehicle.java" if name == "Vehicle" else f"{name}.java"
        result = subprocess.run(["git", "show", f"HEAD:{git_name}"], cwd=ROOT,
                                capture_output=True, check=True, **UTF8)
        write(snapshot / f"src/main/java/garage/{name}.java", result.stdout)
    for name, dest in [("GarageTest.java", "src/test/java/garage/GarageTest.java"),
                       ("pom.xml", "pom.xml"), ("README.md", "README.md")]:
        result = subprocess.run(["git", "show", f"HEAD:{name}"], cwd=ROOT,
                                capture_output=True, check=True, **UTF8)
        write(snapshot / dest, result.stdout)
    current = EVIDENCE / "snapshots/before-final-review"
    shutil.copytree(ROOT / "src", current / "src")
    shutil.copy2(ROOT / "pom.xml", current / "pom.xml")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, **UTF8).strip()
    test_hash = hashlib.sha256((ROOT / "src/test/java/garage/GarageTest.java").read_bytes()).hexdigest()
    write(EVIDENCE / "capture_manifest.json", json.dumps({
        "captured_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat(),
        "repository_commit": commit,
        "supplied_test_sha256": test_hash,
        "original_snapshot_note": "Git HEAD sources relocated into the documented Maven layout; vehicle.java renamed Vehicle.java. Contents unchanged.",
        "before_final_review_note": "Exact current source tree before the final review changes.",
    }, ensure_ascii=False, indent=2) + "\n")
    classes = ROOT / "target/evidence/original-classes"
    classes.mkdir(parents=True, exist_ok=True)
    run_record(["javac", "-g", "-encoding", "UTF-8", "-d", str(classes),
                *map(str, sorted((snapshot / "src/main/java/garage").glob("*.java")))],
               EVIDENCE / "logs/01-original-compile.txt")
    run_record([maven(), "--batch-mode", "--no-transfer-progress", "test"],
               EVIDENCE / "logs/02-before-final-review-tests.txt")


def compile_debug() -> None:
    cp = junit_classpath()
    original = EVIDENCE / "snapshots/repository-original"
    reproduction = EVIDENCE / "snapshots/reproduce-motorcycle-failure"
    if not reproduction.exists():
        shutil.copytree(original, reproduction)
        truck = reproduction / "src/main/java/garage/Truck.java"
        source = truck.read_text(encoding="utf-8")
        old = "        // BUG: never calls super(...), so enteredAt is never set\n"
        if source.count(old) != 1:
            raise ValueError("Unexpected original Truck constructor")
        write(truck, source.replace(old, old + "        super(licensePlate, LocalDateTime.now());\n"))
    for label, source in [("reproduction", reproduction), ("current", ROOT)]:
        classes = ROOT / f"target/evidence/{label}-classes"
        classes.mkdir(parents=True, exist_ok=True)
        sources = sorted((source / "src/main/java/garage").glob("*.java"))
        sources += [source / "src/test/java/garage/GarageTest.java", ROOT / "tools/garage/DebugRunner.java"]
        code = run_record(["javac", "-g", "-encoding", "UTF-8", "-cp", cp, "-d", str(classes),
                           *map(str, sources)], EVIDENCE / f"logs/compile-debug-{label}.txt")
        if code:
            raise RuntimeError(f"Could not compile {label} debug sources")
        write(ROOT / f"target/evidence/{label}-classpath.txt", str(classes) + os.pathsep + cp)
    write(EVIDENCE / "snapshots/reproduce-motorcycle-failure/REPRODUCTION.md",
          "# Reproducing the Motorcycle Failure\n\n"
          "This copy was made from the captured Git HEAD sources. The Maven directory layout and Vehicle.java filename were normalized. "
          "Only `super(licensePlate, LocalDateTime.now());` was added to the Truck constructor to get past the original compilation error. "
          "The Motorcycle and GarageTest contents were preserved. "
          "The evidence was captured by running this reproduction; it is not a capture from an earlier session.\n")


def scenarios(phase: str) -> None:
    sources_by_phase = {
        "before": EVIDENCE / "snapshots/before-final-review",
        "after": ROOT,
        "reproduction": EVIDENCE / "snapshots/reproduce-motorcycle-failure",
    }
    source = sources_by_phase[phase]
    classes = ROOT / f"target/evidence/scenarios-{phase}"
    classes.mkdir(parents=True, exist_ok=True)
    sources = sorted((source / "src/main/java/garage").glob("*.java"))
    sources.append(ROOT / "tools/garage/GarageScenarioChecks.java")
    code = run_record(["javac", "-g", "-encoding", "UTF-8", "-d", str(classes), *map(str, sources)],
                      EVIDENCE / f"logs/compile-scenarios-{phase}.txt")
    if code:
        raise RuntimeError("Scenario compilation failed")
    run_record(["java", "-cp", str(classes), "garage.GarageScenarioChecks"],
               EVIDENCE / f"logs/scenarios-{phase}.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["prepare", "compile-debug", "scenarios-before", "scenarios-after", "scenarios-reproduction"])
    args = parser.parse_args()
    if args.operation == "prepare":
        prepare()
    elif args.operation == "compile-debug":
        compile_debug()
    else:
        scenarios(args.operation.removeprefix("scenarios-"))
