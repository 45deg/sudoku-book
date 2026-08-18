"""A small CNF example solved with MiniSat 2.2 through PySAT."""

from pysat.solvers import Minisat22


# BEGIN article-small-sat
def exactly_one_of_two() -> tuple[tuple[bool, bool], ...]:
    # 1個以上を真にする節と、2個同時には真にしない節です。
    clauses = [[1, 2], [-1, -2]]
    answers: list[tuple[bool, bool]] = []

    with Minisat22(bootstrap_with=clauses) as solver:
        while solver.solve():
            model = solver.get_model()
            positive = {literal for literal in model if literal > 0}
            answer = (1 in positive, 2 in positive)
            answers.append(answer)

            # 今得た真偽値の組を禁止し、次のモデルを探します。
            blocking_clause = [
                -variable if value else variable
                for variable, value in enumerate(answer, start=1)
            ]
            solver.add_clause(blocking_clause)

    return tuple(sorted(answers))
# END article-small-sat


def main() -> None:
    print("formula: (x1 OR x2) AND (NOT x1 OR NOT x2)")
    for number, (x1, x2) in enumerate(exactly_one_of_two(), start=1):
        print(f"model {number}: x1={str(x1).lower()} x2={str(x2).lower()}")


if __name__ == "__main__":
    main()
