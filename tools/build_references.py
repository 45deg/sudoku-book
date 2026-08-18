"""Generate chapter-local Sphinx bibliography directives."""

from __future__ import annotations

import argparse
from pathlib import Path

from pybtex.database import parse_file


def render(database: Path, keys_file: Path) -> str:
    data = parse_file(database)
    keys = [
        line.strip()
        for line in keys_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    missing = [key for key in keys if key not in data.entries]
    if missing:
        raise SystemExit(f"missing BibTeX entries: {', '.join(missing)}")
    entries = "\n".join(f"   {key}" for key in keys)
    return (
        ".. bibliography::\n"
        "   :style: unsrt\n"
        "   :filter: False\n\n"
        f"{entries}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--keys", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render(args.database, args.keys)
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != rendered:
            raise SystemExit(f"generated bibliography is stale: {args.output}")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
