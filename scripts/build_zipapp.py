"""Build a dependency-free offline Python zipapp from the supported package."""
from pathlib import Path
import shutil
import tempfile
import zipapp

root = Path(__file__).resolve().parents[1]
(root / "dist").mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as temporary:
    staged = Path(temporary)
    shutil.copytree(root / "src" / "seedstartgate", staged / "seedstartgate", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (staged / "__main__.py").write_text("from seedstartgate.cli import main\nraise SystemExit(main())\n", encoding="utf-8")
    zipapp.create_archive(staged, root / "dist" / "seedstartgate.pyz", interpreter="/usr/bin/env python3", compressed=True)
print("Built dist/seedstartgate.pyz (requires supported Python; no third-party runtime packages)")
