#!/usr/bin/env python3
"""Create a portable Secret Fire source package without personal save data."""

import argparse
import hashlib
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIRECTORIES = (".agents", "data", "docs", "examples", "prompts", "public", "tests", "tools")
PACKAGE_FILES = (
    ".gitignore", "README.md", "abilities.py", "action-contract.mjs", "adjudication-contract.mjs",
    "dialogue-style.mjs", "engine.py", "example-turn.json", "http-boundary.mjs", "item-rarity-policy.mjs",
    "item_types.py", "narrator-json.mjs", "package.json", "server.mjs",
)
IGNORED_NAMES = {"__pycache__", "node_modules", ".DS_Store", "backups"}


def ignored(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES or name.endswith((".sqlite3", ".sqlite3-wal", ".sqlite3-shm"))}


def write_checksums(package_root: Path) -> None:
    lines: list[str] = []
    for path in sorted(item for item in package_root.rglob("*") if item.is_file() and item.name != "SHA256SUMS.txt"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(package_root)}")
    (package_root / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a source-only Secret Fire delivery zip.")
    parser.add_argument("--output", required=True, help="Output .zip path")
    parser.add_argument("--name", default="Secret-Fire-Project", help="Top-level directory name inside the archive")
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    if output.suffix != ".zip":
        raise SystemExit("Output path must end in .zip")
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="secret-fire-package-") as temporary:
        package_root = Path(temporary) / args.name
        package_root.mkdir()
        for name in PACKAGE_DIRECTORIES:
            shutil.copytree(ROOT / name, package_root / name, ignore=ignored)
        for name in PACKAGE_FILES:
            shutil.copy2(ROOT / name, package_root / name)
        write_checksums(package_root)
        archive_base = output.with_suffix("")
        made = Path(shutil.make_archive(str(archive_base), "zip", root_dir=Path(temporary), base_dir=args.name))
        if made != output:
            made.replace(output)
    print(f"Created {output}")


if __name__ == "__main__":
    main()
