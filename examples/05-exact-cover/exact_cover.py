"""A small, generic implementation of Algorithm X."""

from __future__ import annotations

from collections.abc import Collection, Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

RowId = TypeVar("RowId", bound=Hashable)
ColumnId = TypeVar("ColumnId", bound=Hashable)


@dataclass
class SearchStats:
    nodes: int = 0
    branches: int = 0
    dead_ends: int = 0


@dataclass
class ExactCoverResult(Generic[RowId]):
    solutions: tuple[tuple[RowId, ...], ...]
    exhausted: bool
    stats: SearchStats


def build_columns(
    rows: Mapping[RowId, Collection[ColumnId]],
    required_columns: Iterable[ColumnId] | None = None,
) -> dict[ColumnId, set[RowId]]:
    columns = {column: set() for column in required_columns or ()}
    for row, covered in rows.items():
        for column in covered:
            columns.setdefault(column, set()).add(row)
    return columns


# BEGIN article-algorithm-x
def algorithm_x(
    rows: Mapping[RowId, Collection[ColumnId]],
    columns: Mapping[ColumnId, set[RowId]],
    limit: int,
    chosen: list[RowId],
    solutions: list[tuple[RowId, ...]],
    stats: SearchStats,
) -> bool:
    """解がlimit個集まったらTrue、探索を終えたらFalseを返す。"""
    stats.nodes += 1
    if not columns:
        # すべての列を一度ずつ覆えたので、選択した行が解になる。
        solutions.append(tuple(chosen))
        return len(solutions) >= limit

    # 選べる行が最も少ない列から調べ、早めに矛盾を見つける。
    column = min(columns, key=lambda item: (len(columns[item]), repr(item)))
    candidates = columns[column]
    if not candidates:
        stats.dead_ends += 1
        return False

    for row in sorted(candidates, key=repr):
        stats.branches += 1
        covered = rows[row]

        # 選んだ行と一つでも列を共有する行は、同時には選べない。
        conflicts = set().union(*(columns[item] for item in covered))
        next_columns = {
            item: available - conflicts
            for item, available in columns.items()
            if item not in covered
        }

        chosen.append(row)
        stop = algorithm_x(rows, next_columns, limit, chosen, solutions, stats)
        chosen.pop()
        if stop:
            return True

    return False
# END article-algorithm-x


def solve_exact_cover(
    rows: Mapping[RowId, Collection[ColumnId]],
    limit: int = 1,
    required_columns: Iterable[ColumnId] | None = None,
) -> ExactCoverResult[RowId]:
    if limit < 1:
        raise ValueError("limit must be positive")

    columns = build_columns(rows, required_columns)
    solutions: list[tuple[RowId, ...]] = []
    stats = SearchStats()
    stopped_at_limit = algorithm_x(rows, columns, limit, [], solutions, stats)
    return ExactCoverResult(tuple(solutions), not stopped_at_limit, stats)

