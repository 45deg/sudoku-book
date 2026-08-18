"""Generate or verify citations for every chapter key file."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_references import render


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    database = root / "bibliography" / "references.bib"
    keys_dir = root / "bibliography" / "chapter-keys"
    output_dir = root / "bibliography" / "generated"
    key_files = sorted(keys_dir.glob("*.txt"))
    if not key_files:
        raise SystemExit(f"no chapter key files found in {keys_dir}")

    stale: list[str] = []
    for keys_file in key_files:
        output = output_dir / f"{keys_file.stem}.rst"
        expected = render(database, keys_file)
        if args.check:
            current = output.read_text(encoding="utf-8") if output.exists() else ""
            if current != expected:
                stale.append(str(output.relative_to(root)))
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
            output.write_text(expected, encoding="utf-8")

    if stale:
        raise SystemExit("stale generated bibliographies: " + ", ".join(stale))
    action = "checked" if args.check else "generated"
    print(f"{action} {len(key_files)} chapter bibliographies")


if __name__ == "__main__":
    main()
