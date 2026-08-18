"""Sample a 4x4 Sudoku QUBO with classical simulated annealing."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import dimod
import neal

from qubo import Board, SIZE, build_qubo, variable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import format_board, load_board, validate_solution  # noqa: E402

DEFAULT_SEED = 20260808
DEFAULT_READS = 500
DEFAULT_SWEEPS = 2000


@dataclass(frozen=True)
class SamplingResult:
    status: str
    best_energy: float
    zero_energy_reads: int
    solutions: tuple[Board, ...]


def decode_sample(sample: dimod.SampleView) -> Board | None:
    values: list[int] = []
    for row in range(SIZE):
        for column in range(SIZE):
            selected = [
                digit
                for digit in range(1, SIZE + 1)
                if sample[variable(row, column, digit)] == 1
            ]
            if len(selected) != 1:
                return None
            values.append(selected[0])
    return tuple(values)


# BEGIN article-sampling
def sample_sudoku(givens: Board, *, seed: int, reads: int, sweeps: int) -> SamplingResult:
    bqm = build_qubo(givens)
    sampler = neal.SimulatedAnnealingSampler()

    # 同じ乱数シード、読み出し回数、スイープ数なら実行条件を再現できる。
    samples = sampler.sample(
        bqm,
        seed=seed,
        num_reads=reads,
        num_sweeps=sweeps,
    ).aggregate()

    valid_boards: set[Board] = set()
    zero_energy_reads = 0
    for datum in samples.data(fields=["sample", "energy", "num_occurrences"]):
        if abs(datum.energy) > 1e-9:
            continue
        zero_energy_reads += datum.num_occurrences

        board = decode_sample(datum.sample)
        if board is None:
            continue
        valid, _ = validate_solution(board, givens)
        if valid:
            valid_boards.add(board)

    # 焼きなましでゼロエネルギー解を見つけられなくても、unsatとは断定しない。
    status = "solved" if valid_boards else "unknown"
    return SamplingResult(
        status=status,
        best_energy=float(samples.first.energy),
        zero_energy_reads=zero_energy_reads,
        solutions=tuple(sorted(valid_boards)),
    )
# END article-sampling


def render_result(
    givens: Board,
    *,
    seed: int,
    reads: int,
    sweeps: int,
    limit: int,
) -> str:
    result = sample_sudoku(givens, seed=seed, reads=reads, sweeps=sweeps)
    shown = result.solutions[:limit]
    evidence = "at-least-two" if len(result.solutions) >= 2 else "unknown"
    lines = [
        f"status: {result.status}",
        "sampler: neal.SimulatedAnnealingSampler",
        f"variables: {SIZE * SIZE * SIZE}",
        f"seed: {seed}",
        f"reads: {reads}",
        f"sweeps: {sweeps}",
        f"best_energy: {result.best_energy:.1f}",
        f"zero_energy_reads: {result.zero_energy_reads}",
        f"distinct_valid_solutions_found: {len(result.solutions)}",
        f"multiplicity_evidence: {evidence}",
        f"shown: {len(shown)}",
    ]
    for index, board in enumerate(shown, start=1):
        lines.extend((f"solution {index}:", format_board(board)))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="QUBOを焼きなましでサンプリングします")
    parser.add_argument("board", type=Path)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--reads", type=int, default=DEFAULT_READS)
    parser.add_argument("--sweeps", type=int, default=DEFAULT_SWEEPS)
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()
    if args.reads < 1 or args.sweeps < 1 or args.limit < 0:
        parser.error("readsとsweepsは1以上、limitは0以上にしてください")

    givens = load_board(args.board)
    print(
        render_result(
            givens,
            seed=args.seed,
            reads=args.reads,
            sweeps=args.sweeps,
            limit=args.limit,
        )
    )


if __name__ == "__main__":
    main()
