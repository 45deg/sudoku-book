"""Parse every manuscript with Docutils and fail on warnings."""

from __future__ import annotations

import argparse
import io
import tempfile
from pathlib import Path

from docutils.core import publish_file


def manuscript_paths(root: Path) -> list[Path]:
    paths = [root / "index.rst", root / "AUTHORING.rst", root / "chapter-template.rst"]
    paths.extend(sorted((root / "chapters").glob("*.rst")))
    paths.extend(sorted((root / "appendices").glob("*.rst")) if (root / "appendices").exists() else [])
    return [path for path in paths if path.exists()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="sudoku-rst-") as destination:
        for source in manuscript_paths(args.root):
            warnings = io.StringIO()
            try:
                publish_file(
                    source_path=str(source),
                    destination_path=str(Path(destination) / f"{source.stem}.html"),
                    writer_name="html5",
                    settings_overrides={
                        "warning_stream": warnings,
                        "report_level": 1,
                        "halt_level": 2,
                        "file_insertion_enabled": True,
                        "raw_enabled": False,
                    },
                )
            except Exception as exc:  # Docutils raises several SystemMessage subclasses.
                failures.append(f"{source.relative_to(args.root)}: {exc}")
            warning_text = warnings.getvalue().strip()
            if warning_text:
                failures.append(f"{source.relative_to(args.root)}:\n{warning_text}")

    if failures:
        raise SystemExit("\n\n".join(failures))
    print(f"checked {len(manuscript_paths(args.root))} reStructuredText files")


if __name__ == "__main__":
    main()
