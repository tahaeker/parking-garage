"""Create a portable submission archive without Git metadata or build outputs."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission"
OUTPUT.mkdir(exist_ok=True)
archive = OUTPUT / "Taha_Yasin_Eker_230201042_OOP.zip"
excluded = {".git", "target", ".idea", "__pycache__", "submission"}
files = sorted(path for path in ROOT.rglob("*")
               if path.is_file() and not any(part in excluded for part in path.relative_to(ROOT).parts)
               and path.suffix not in {".iml", ".pyc"})
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    for path in files:
        bundle.write(path, "parking-garage/" + path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as bundle:
    if bundle.testzip() is not None:
        raise AssertionError("Archive integrity check failed")
    for path in files:
        name = "parking-garage/" + path.relative_to(ROOT).as_posix()
        if bundle.read(name) != path.read_bytes():
            raise AssertionError(f"Archive content mismatch: {name}")
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(OUTPUT / "SHA256.txt").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
print(f"Archive: {archive}\nFiles: {len(files)}\nBytes: {archive.stat().st_size}\nSHA-256: {digest}")
