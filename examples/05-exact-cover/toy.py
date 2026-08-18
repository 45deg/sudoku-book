"""A four-column exact-cover example used in the article."""

from __future__ import annotations

from exact_cover import solve_exact_cover

ROWS = {
    "r1": ("A", "C"),
    "r2": ("B", "D"),
    "r3": ("A", "D"),
    "r4": ("B", "C"),
}
COLUMNS = ("A", "B", "C", "D")


def main() -> None:
    result = solve_exact_cover(ROWS, limit=10, required_columns=COLUMNS)
    print("columns: A B C D")
    for row, covered in ROWS.items():
        print(f"{row}: {' '.join(covered)}")
    print(f"solutions: {len(result.solutions)}")
    for number, solution in enumerate(result.solutions, start=1):
        print(f"solution {number}: {' '.join(solution)}")
    print(f"nodes: {result.stats.nodes}")
    print(f"branches: {result.stats.branches}")


if __name__ == "__main__":
    main()

