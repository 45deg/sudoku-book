"""Shared board parsing and validation for the article examples."""

from __future__ import annotations

from math import isqrt
from pathlib import Path
from typing import Iterable

Board = tuple[int, ...]


def board_geometry(board: Board) -> tuple[int, int]:
    """Return ``(side, box_side)`` for a square Sudoku board."""
    side = isqrt(len(board))
    if side * side != len(board):
        raise ValueError("the board must contain side^2 cells")
    box_side = isqrt(side)
    if box_side * box_side != side:
        raise ValueError("the side length must have a square box size")
    return side, box_side


def parse_board(text: str) -> Board:
    """Parse digits, ``0``, or ``.`` while ignoring other whitespace."""
    cells: list[int] = []
    for char in text:
        if char in "0.":
            cells.append(0)
        elif char.isdigit():
            cells.append(int(char))
        elif char.isspace():
            continue
        else:
            raise ValueError(f"unexpected board character: {char!r}")

    board = tuple(cells)
    side, _ = board_geometry(board)
    if side not in (4, 9):
        raise ValueError("the examples support 4x4 and 9x9 boards")
    if any(value < 0 or value > side for value in board):
        raise ValueError(f"digits must be between 0 and {side}")
    return board


def load_board(path: str | Path) -> Board:
    return parse_board(Path(path).read_text(encoding="utf-8"))


def format_board(board: Board) -> str:
    """Format a board as plain rows, using ``.`` for empty cells."""
    side, _ = board_geometry(board)
    rows = []
    for start in range(0, len(board), side):
        rows.append("".join(str(value) if value else "." for value in board[start : start + side]))
    return "\n".join(rows)


def units(board: Board) -> tuple[tuple[int, ...], ...]:
    side, box_side = board_geometry(board)
    result: list[tuple[int, ...]] = []
    result.extend(tuple(row * side + col for col in range(side)) for row in range(side))
    result.extend(tuple(row * side + col for row in range(side)) for col in range(side))
    for box_row in range(0, side, box_side):
        for box_col in range(0, side, box_side):
            result.append(
                tuple(
                    row * side + col
                    for row in range(box_row, box_row + box_side)
                    for col in range(box_col, box_col + box_side)
                )
            )
    return tuple(result)


def is_consistent_partial(board: Board) -> bool:
    """Return whether no filled digit is duplicated in a unit."""
    side, _ = board_geometry(board)
    for unit in units(board):
        values = [board[index] for index in unit if board[index] != 0]
        if any(value > side for value in values) or len(values) != len(set(values)):
            return False
    return True


def validate_solution(solution: Board, givens: Board) -> tuple[bool, tuple[str, ...]]:
    """Validate completeness, givens, and every row, column, and box."""
    errors: list[str] = []
    if len(solution) != len(givens):
        return False, ("solution and givens have different sizes",)

    side, _ = board_geometry(solution)
    expected = set(range(1, side + 1))

    for index, given in enumerate(givens):
        if given and solution[index] != given:
            errors.append(f"cell {index} does not preserve given {given}")

    if any(value == 0 for value in solution):
        errors.append("solution still contains empty cells")

    for number, unit in enumerate(units(solution), start=1):
        values = {solution[index] for index in unit}
        if values != expected:
            errors.append(f"unit {number} is not a permutation of 1..{side}")

    return not errors, tuple(errors)


def boards_are_distinct(boards: Iterable[Board]) -> bool:
    materialized = tuple(boards)
    return len(materialized) == len(set(materialized))
