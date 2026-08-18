"""Use one kanren relation in more than one direction."""

from kanren import conde, eq, run, var, vars
from kanren.goals import appendo


# BEGIN article-appendo
def append_examples() -> tuple[object, object]:
    whole = var("whole")

    # 左右の列が既知なら、結合後の列を求めます。
    joined = run(1, whole, appendo((1, 2), (3,), whole))

    left, right = vars(2)
    # 結合後の列だけを与えると、同じ関係から分割位置を列挙できます。
    splits = run(0, (left, right), appendo(left, right, (1, 2, 3)))
    return joined, splits
# END article-appendo


# BEGIN article-choice
def choice_example() -> tuple[int, ...]:
    number = var("number")
    # condeの各組は選択肢です。ここでは1または2という二つの答えを作ります。
    goal = conde((eq(number, 1),), (eq(number, 2),))
    return run(0, number, goal)
# END article-choice


def main() -> None:
    joined, splits = append_examples()
    print(f"join: {joined[0]}")
    print("splits:")
    for left, right in splits:
        print(f"  {left} + {right}")
    print()
    print(f"choices: {choice_example()}")


if __name__ == "__main__":
    main()
