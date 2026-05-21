#!/usr/bin/env python3
import itertools
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import yaml


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def build_entries(matrix):
    entries = []

    boards = as_list(matrix.get("board"))
    shields = as_list(matrix.get("shield")) or [None]

    for board, shield in itertools.product(boards, shields):
        entry = {"board": board}
        if shield:
            entry["shield"] = shield
        entries.append(entry)

    entries.extend(matrix.get("include", []))
    return entries


def run(command, cwd):
    print("+ " + shlex.join(str(part) for part in command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main():
    repo_root = Path.cwd()
    local_dir = repo_root / ".local"
    work_dir = local_dir / "zmk-work"
    config_dir = work_dir / "config"
    output_dir = local_dir / "firmware"
    home_dir = local_dir / "home"

    home_dir.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(home_dir)

    matrix = yaml.safe_load((repo_root / "build.yaml").read_text())
    entries = build_entries(matrix)

    if not entries:
        raise SystemExit("No build entries found in build.yaml")

    if config_dir.exists():
        shutil.rmtree(config_dir)
    shutil.copytree(repo_root / "config", config_dir)

    work_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not (work_dir / ".west").exists():
        run(["west", "init", "-l", str(config_dir)], cwd=work_dir)
    else:
        run(["west", "config", "manifest.path", "config"], cwd=work_dir)

    run(["git", "config", "--global", "--add", "safe.directory", "*"], cwd=work_dir)
    run(["west", "update", "--fetch-opt=--filter=tree:0"], cwd=work_dir)
    run(["west", "zephyr-export"], cwd=work_dir)

    for entry in entries:
        board = entry["board"]
        shield = entry.get("shield")
        snippet = entry.get("snippet")
        artifact_name = entry.get("artifact-name") or f"{shield + '-' if shield else ''}{board}-zmk"
        build_dir = work_dir / "build" / artifact_name

        if build_dir.exists():
            shutil.rmtree(build_dir)

        command = ["west", "build", "-s", "zmk/app", "-d", str(build_dir), "-b", board]
        if snippet:
            command.extend(["-S", snippet])

        command.extend(["--", f"-DZMK_CONFIG={config_dir}"])
        if shield:
            command.append(f"-DSHIELD={shield}")
        if entry.get("cmake-args"):
            command.extend(shlex.split(entry["cmake-args"]))

        print(f"\nBuilding {artifact_name}", flush=True)
        run(command, cwd=work_dir)

        uf2 = build_dir / "zephyr" / "zmk.uf2"
        binary = uf2 if uf2.exists() else build_dir / "zephyr" / "zmk.bin"
        if not binary.exists():
            raise SystemExit(f"No firmware artifact found for {artifact_name}")

        suffix = binary.suffix
        output = output_dir / f"{artifact_name}{suffix}"
        shutil.copy2(binary, output)
        print(f"Wrote {output}", flush=True)


if __name__ == "__main__":
    main()
