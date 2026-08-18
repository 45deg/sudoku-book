#!/usr/bin/env python3
"""Run the small reachability model with nuXmv IC3."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from solve import check_invariant, find_nuxmv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--nuxmv")
    args = parser.parse_args()

    nuxmv = find_nuxmv(args.nuxmv)
    model_path = Path(__file__).with_name("small_example.smv")
    result = check_invariant(model_path.read_text(encoding="utf-8"), nuxmv, bound=2)
    rooms = re.findall(r"room = (entrance|hall|goal)", result.output)
    print("property: goal is unreachable")
    print(f"result: {'false' if result.outcome == 'counterexample' else result.outcome}")
    if rooms:
        print("counterexample: " + " -> ".join(rooms))


if __name__ == "__main__":
    main()
