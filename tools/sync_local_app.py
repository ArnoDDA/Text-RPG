#!/usr/bin/env python3
"""Stage and replace the macOS local runtime from this source tree.

Personal saves are intentionally not part of this operation. The server keeps
them in ~/.codex-rpg-memory unless CAMPAIGN_DB is explicitly configured.
"""

import argparse
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIRECTORIES = (".agents", "data", "prompts", "public", "tools")
RUNTIME_FILES = (
    "abilities.py", "action-contract.mjs", "adjudication-contract.mjs", "engine.py",
    "dialogue-style.mjs", "http-boundary.mjs", "item-rarity-policy.mjs", "item_types.py", "narrator-json.mjs", "package.json", "server.mjs",
)
IGNORED_NAMES = {"__pycache__", "node_modules", ".DS_Store", "backups"}


def ignore_runtime_files(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES or name.endswith((".sqlite3", ".sqlite3-wal", ".sqlite3-shm"))}


def copy_runtime(destination: Path) -> int:
    copied = 0
    for name in RUNTIME_DIRECTORIES:
        source = ROOT / name
        if not source.is_dir():
            raise FileNotFoundError(f"Required runtime directory is missing: {source}")
        shutil.copytree(source, destination / name, ignore=ignore_runtime_files)
        copied += sum(1 for item in (destination / name).rglob("*") if item.is_file())
    for name in RUNTIME_FILES:
        source = ROOT / name
        if not source.is_file():
            raise FileNotFoundError(f"Required runtime file is missing: {source}")
        shutil.copy2(source, destination / name)
        copied += 1
    return copied


def restart_service() -> None:
    label = "com.secretfire.local-game"
    subprocess.run(
        ["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{label}"],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish this source tree to the local Secret Fire runtime.")
    parser.add_argument(
        "--destination",
        default=str(Path.home() / "Library" / "Application Support" / "Secret Fire" / "app"),
        help="Runtime directory to replace",
    )
    parser.add_argument("--replace", action="store_true", help="Required when the destination already exists")
    parser.add_argument("--restart", action="store_true", help="Restart the per-user LaunchAgent (the default behavior)")
    parser.add_argument("--no-restart", action="store_true", help="Publish files without restarting the per-user LaunchAgent")
    args = parser.parse_args()

    destination = Path(args.destination).expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise SystemExit("Destination must be outside the source tree")
    if destination.exists() and not args.replace:
        raise SystemExit(f"Destination already exists: {destination}. Re-run with --replace after reviewing it.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = destination.parent / f".{destination.name}.stage-{uuid.uuid4().hex}"
    previous = destination.parent / f".{destination.name}.previous-{uuid.uuid4().hex}"
    try:
        stage.mkdir()
        copied = copy_runtime(stage)
        if destination.exists():
            destination.replace(previous)
        stage.replace(destination)
        if previous.exists():
            shutil.rmtree(previous)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        if previous.exists() and not destination.exists():
            previous.replace(destination)
        raise
    if not args.no_restart:
        restart_service()
    print(f"Published {copied} runtime files to {destination}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Publish failed: {error}", file=sys.stderr)
        raise SystemExit(1)
