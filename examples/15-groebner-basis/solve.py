"""Solve strongly constrained 4x4 Sudoku instances with a Gröbner basis."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from sympy import Expr, Integer, QQ, Symbol, groebner, solve_poly_system

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import Board, format_board, load_board, units, validate_solution  # noqa: E402

SIZE = 4
Candidate = tuple[int, int]


def variable_name(position: int, digit: int) -> str:
    row, column = divmod(position, SIZE)
    return f"x_{row + 1}_{column + 1}_{digit}"


@dataclass(frozen=True)
class PolynomialModel:
    givens: Board
    variables: tuple[Symbol, ...]
    candidate_variables: dict[Candidate, Symbol]
    polynomials: tuple[Expr, ...]


@dataclass(frozen=True)
class SolveResult:
    status: str
    variables: int
    input_polynomials: int
    basis: tuple[Expr, ...]
    solutions: tuple[Board, ...]


# BEGIN article-model
def build_polynomial_model(givens: Board) -> PolynomialModel:
    if len(givens) != SIZE * SIZE:
        raise ValueError("この例は4×4数独だけを扱います")

    sudoku_units = units(givens)
    polynomials: list[Expr] = []

    # 初期配置だけで同じ数字が重複していれば、1 = 0を加えて矛盾を表す。
    for unit in sudoku_units:
        fixed = [givens[position] for position in unit if givens[position]]
        if len(fixed) != len(set(fixed)):
            polynomials.append(Integer(1))

    candidate_digits: dict[int, tuple[int, ...]] = {}
    for position, given in enumerate(givens):
        if given:
            continue
        related = {
            other
            for unit in sudoku_units
            if position in unit
            for other in unit
        }
        candidate_digits[position] = tuple(
            digit
            for digit in range(1, SIZE + 1)
            if all(givens[other] != digit for other in related)
        )

    candidate_keys = tuple(
        (position, digit)
        for position in sorted(candidate_digits)
        for digit in candidate_digits[position]
    )
    variables = tuple(Symbol(variable_name(*key)) for key in candidate_keys)
    candidate_variables = dict(zip(candidate_keys, variables, strict=True))

    # x(x - 1) = 0を加え、各候補変数を0または1に限る。
    polynomials.extend(variable * (variable - 1) for variable in variables)

    # 各空きマスでは、残った候補変数の和を1にする。
    for position, digits in candidate_digits.items():
        choices = [candidate_variables[position, digit] for digit in digits]
        polynomials.append(sum(choices, Integer(0)) - 1)

    # 行、列、ブロックごとに、まだ置かれていない数字を一度だけ選ぶ。
    for unit in sudoku_units:
        for digit in range(1, SIZE + 1):
            fixed_count = sum(givens[position] == digit for position in unit)
            if fixed_count > 1:
                polynomials.append(Integer(1))
            elif fixed_count == 0:
                choices = [
                    candidate_variables[position, digit]
                    for position in unit
                    if (position, digit) in candidate_variables
                ]
                polynomials.append(sum(choices, Integer(0)) - 1)

    return PolynomialModel(
        givens=givens,
        variables=variables,
        candidate_variables=candidate_variables,
        polynomials=tuple(polynomials),
    )
# END article-model


def decode_solution(model: PolynomialModel, values: tuple[Expr, ...]) -> Board:
    assignment = dict(zip(model.variables, values, strict=True))
    board = list(model.givens)
    for position, given in enumerate(model.givens):
        if given:
            continue
        selected = [
            digit
            for digit in range(1, SIZE + 1)
            if (variable := model.candidate_variables.get((position, digit))) is not None
            and assignment[variable] == 1
        ]
        if len(selected) != 1:
            raise ValueError("多項式解から一つの数字を復元できません")
        board[position] = selected[0]
    return tuple(board)


# BEGIN article-solving
def solve(givens: Board) -> SolveResult:
    model = build_polynomial_model(givens)

    if not model.variables:
        valid, _ = validate_solution(givens, givens)
        return SolveResult(
            status="solved" if valid else "unsat",
            variables=0,
            input_polynomials=len(model.polynomials),
            basis=() if valid else (Integer(1),),
            solutions=(givens,) if valid else (),
        )

    # 辞書式順序の被約Gröbner基底を、有理数係数で正確に計算する。
    computed = groebner(
        model.polynomials,
        *model.variables,
        order="lex",
        domain=QQ,
    )
    basis = tuple(polynomial.as_expr() for polynomial in computed.polys)

    # 基底が[1]なら連立方程式は1 = 0を含み、共通解を持たない。
    if basis == (Integer(1),):
        return SolveResult(
            status="unsat",
            variables=len(model.variables),
            input_polynomials=len(model.polynomials),
            basis=basis,
            solutions=(),
        )

    # Boolean方程式を含む零次元系なので、基底から全ての根を厳密に求める。
    roots = solve_poly_system(
        basis,
        *model.variables,
        strict=True,
    )
    if roots is None:
        raise ValueError("Gröbner基底から解を復元できません")

    solutions: set[Board] = set()
    for root in roots:
        if any(value not in (0, 1) for value in root):
            raise ValueError("Boolean方程式に0、1以外の根が返されました")
        board = decode_solution(model, root)
        valid, errors = validate_solution(board, givens)
        if not valid:
            raise ValueError("共通検証器が完成盤面を拒否しました: " + "; ".join(errors))
        solutions.add(board)

    return SolveResult(
        status="solved" if solutions else "unsat",
        variables=len(model.variables),
        input_polynomials=len(model.polynomials),
        basis=basis,
        solutions=tuple(sorted(solutions)),
    )
# END article-solving


def render_result(givens: Board, *, limit: int, basis_limit: int) -> str:
    result = solve(givens)
    shown_basis = result.basis[:basis_limit]
    shown_solutions = result.solutions[:limit]
    lines = [
        f"status: {result.status}",
        "coefficient_domain: QQ",
        "monomial_order: lex",
        f"variables: {result.variables}",
        f"input_polynomials: {result.input_polynomials}",
        f"basis_polynomials: {len(result.basis)}",
        f"basis_shown: {len(shown_basis)}",
    ]
    if shown_basis:
        lines.append("basis:")
        lines.extend(f"  {polynomial} = 0" for polynomial in shown_basis)
    lines.extend(
        (
            f"solution_count: {len(result.solutions)}",
            f"shown: {len(shown_solutions)}",
        )
    )
    for index, board in enumerate(shown_solutions, start=1):
        lines.extend((f"solution {index}:", format_board(board)))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Boolean多項式のGröbner基底で4×4数独を解きます")
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--basis-limit", type=int, default=0)
    args = parser.parse_args()
    if args.limit < 0 or args.basis_limit < 0:
        parser.error("limitとbasis-limitには0以上を指定してください")

    print(
        render_result(
            load_board(args.board),
            limit=args.limit,
            basis_limit=args.basis_limit,
        )
    )


if __name__ == "__main__":
    main()
