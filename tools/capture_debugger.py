"""Record jdb output and real variable values from individual supplied tests."""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
import queue
import re
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "trace_evidence"


class Debugger:
    def __init__(self, label: str, scenario: str):
        cp = (ROOT / f"target/evidence/{label}-classpath.txt").read_text(encoding="utf-8")
        source = EVIDENCE / "snapshots/reproduce-motorcycle-failure" if label == "reproduction" else ROOT
        sourcepath = os.pathsep.join(str(p) for p in [source / "src/main/java", source / "src/test/java", ROOT / "tools"])
        command = ["jdb", "-classpath", cp, "-sourcepath", sourcepath, "garage.DebugRunner", scenario]
        self.record = [f"Captured: {dt.datetime.now(dt.timezone(dt.timedelta(hours=3))).isoformat()}\n",
                       f"Source state: {label}\nScenario: {scenario}\n",
                       f"Command: {subprocess.list2cmdline(command)}\n\n"]
        self.output = ""
        self.cursor = 0
        self.queue: queue.Queue[str | None] = queue.Queue()
        self.process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, encoding="utf-8", errors="replace", bufsize=1)
        def read():
            while True:
                character = self.process.stdout.read(1)
                if not character:
                    break
                self.queue.put(character)
            self.queue.put(None)
        threading.Thread(target=read, daemon=True).start()

    def wait(self, pattern: str, timeout: float = 25) -> None:
        deadline = time.monotonic() + timeout
        while True:
            match = re.search(pattern, self.output[self.cursor:])
            if match:
                self.cursor += match.end()
                return
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"No debugger response matching {pattern!r}: {self.output[-2000:]}")
            try:
                character = self.queue.get(timeout=min(remaining, 1))
            except queue.Empty:
                continue
            if character is None:
                raise RuntimeError(f"Debugger exited before {pattern!r}: {self.output[-2000:]}")
            self.output += character
            self.record.append(character)

    def command(self, command: str, response: str = r"main\[\d+\] ") -> None:
        self.record.append(command + "\n")
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        self.wait(response)

    def finish(self, path: Path) -> None:
        try:
            if self.process.poll() is None:
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=5)
        finally:
            if self.process.poll() is None:
                self.process.kill()
            while True:
                try:
                    character = self.queue.get(timeout=0.2)
                    if character is None:
                        break
                    self.record.append(character)
                except queue.Empty:
                    break
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(self.record), encoding="utf-8", newline="\n")
            print(path.relative_to(ROOT))


def capture_motorcycle(label: str) -> None:
    debugger = Debugger(label, "motorcycle")
    try:
        debugger.wait(r"> ")
        debugger.command("stop in garage.Motorcycle.fitsInSpot", r"> ")
        debugger.command("run")
        debugger.command("where")
        debugger.command("locals")
        debugger.command("print spot")
        debugger.command("dump this")
        debugger.command("print this.licensePlate")
        debugger.command("print this.enteredAt.toString()")
        debugger.command("next")
        if label == "reproduction":
            debugger.command("where")
            debugger.command("locals")
            debugger.command("cont", r"The application exited")
        else:
            debugger.command("next")
            debugger.command("where")
            debugger.command("cont", r"The application exited")
    finally:
        debugger.finish(EVIDENCE / f"debugger/motorcycle-{label}.txt")


def capture_truck() -> None:
    debugger = Debugger("current", "truck")
    try:
        debugger.wait(r"> ")
        debugger.command("stop at garage.Vehicle:35", r"> ")
        debugger.command("run")
        debugger.command("where")
        debugger.command("locals")
        debugger.command("print this.licensePlate")
        debugger.command("print this.enteredAt")
        debugger.command("print this.enteredAt.toString()")
        debugger.command("print this.enteredAt != null")
        debugger.command("next")
        debugger.command("cont")
        debugger.command("where")
        debugger.command("cont", r"The application exited")
    finally:
        debugger.finish(EVIDENCE / "debugger/truck-current.txt")


if __name__ == "__main__":
    capture_motorcycle("reproduction")
    capture_motorcycle("current")
    capture_truck()
