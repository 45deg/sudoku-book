"""Render the standalone reStructuredText manuscripts as a small HTML site."""

from __future__ import annotations

import argparse
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from docutils.core import publish_file


def sources(root: Path) -> list[tuple[Path, Path]]:
    result = [(root / "index.rst", Path("index.html"))]
    result.extend(
        (source, Path("chapters") / f"{source.stem}.html")
        for source in sorted((root / "chapters").glob("*.rst"))
    )
    if (root / "appendices").exists():
        result.extend(
            (source, Path("appendices") / f"{source.stem}.html")
            for source in sorted((root / "appendices").glob("*.rst"))
        )
    return result


def rewrite_rst_links(html_path: Path) -> None:
    html = html_path.read_text(encoding="utf-8")
    html = re.sub(r'href="([^"]+)\.rst([#?][^"]*)?"', r'href="\1.html\2"', html)
    html_path.write_text(html, encoding="utf-8")


class LocalResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.resources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and name in {"href", "src"}:
                self.resources.append(value)


def verify_local_resources(output: Path) -> None:
    failures: list[str] = []
    for html_path in sorted(output.rglob("*.html")):
        parser = LocalResourceParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for resource in parser.resources:
            parsed = urlsplit(resource)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (html_path.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                failures.append(
                    f"{html_path.relative_to(output)}: missing local resource {resource}"
                )
    if failures:
        raise SystemExit("\n".join(failures))


def render(root: Path, output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    stylesheet = root / "tools" / "article.css"
    for source, relative_destination in sources(root):
        destination = output / relative_destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        publish_file(
            source_path=str(source),
            destination_path=str(destination),
            writer_name="html5",
            settings_overrides={
                "stylesheet_path": str(stylesheet),
                "embed_stylesheet": True,
                "math_output": "MathML",
                "syntax_highlight": "short",
                "file_insertion_enabled": True,
                "raw_enabled": False,
                "report_level": 2,
                "halt_level": 2,
            },
        )
        rewrite_rst_links(destination)

    if (root / "figures").exists():
        shutil.copytree(root / "figures", output / "figures")

    verify_local_resources(output)
    print(f"rendered {len(sources(root))} pages to {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output or root / "build").resolve()
    render(root, output)


if __name__ == "__main__":
    main()
