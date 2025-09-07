"""Simple cleanup scan helper.

This script is a lightweight aid for developers to quickly locate common
issues when performing repository maintenance.  It intentionally avoids
performing any writes; it merely prints findings to stdout.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=False)


def main() -> None:
    run(["ruff", "--select", "F401,F841", str(ROOT / "mutants2")])
    run(
        [
            "rg",
            "bug_skin_armour|attack|old travel",
            str(ROOT / "mutants2"),
        ]
    )
    run(["rg", "print\(", str(ROOT / "mutants2" / "engine")])
    run(["rg", ",", str(ROOT / "mutants2")])


if __name__ == "__main__":
    main()
