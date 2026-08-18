"""Enumerate stable models of the small choice-rule example."""

from __future__ import annotations

from pathlib import Path

import clingo

PROGRAM = Path(__file__).with_name("choice.lp")


def models() -> tuple[tuple[str, ...], ...]:
    control = clingo.Control(["--warn=none", "--models=0"])
    control.load(str(PROGRAM))
    control.ground([("base", [])])
    answers: list[tuple[str, ...]] = []
    with control.solve(yield_=True) as handle:
        for model in handle:
            answers.append(tuple(sorted(map(str, model.symbols(shown=True)))))
    return tuple(sorted(answers))


def main() -> None:
    answers = models()
    print(f"clingo: {clingo.__version__}")
    print(f"models: {len(answers)}")
    for number, answer in enumerate(answers, start=1):
        print(f"answer {number}: {' '.join(answer)}")


if __name__ == "__main__":
    main()

