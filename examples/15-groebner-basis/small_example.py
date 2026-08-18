"""Compute a lexicographic Gröbner basis for an exactly-one condition."""

from sympy import QQ, groebner, solve_poly_system, symbols


def main() -> None:
    x, y = symbols("x y")
    equations = (
        x**2 - x,
        y**2 - y,
        x + y - 1,
    )

    # 辞書式順序ではxをyより先に置き、yだけの式が基底に現れるようにする。
    basis = groebner(equations, x, y, order="lex", domain=QQ)

    print("input equations:")
    for equation in equations:
        print(f"  {equation} = 0")
    print("groebner basis (lex, x > y):")
    for polynomial in basis.polys:
        print(f"  {polynomial.as_expr()} = 0")

    # 基底は元の連立方程式と同じ解を持つので、基底から二解を復元できる。
    solutions = solve_poly_system(
        [polynomial.as_expr() for polynomial in basis.polys],
        x,
        y,
        strict=True,
    )
    print("solutions:")
    for solution in solutions:
        print(f"  x={solution[0]}, y={solution[1]}")


if __name__ == "__main__":
    main()
