"""「二変数から一つだけ選ぶ」罰則の全入力を表示します。"""


def penalty(first: int, second: int) -> int:
    """Return ``(first + second - 1)^2``."""
    return (first + second - 1) ** 2


def main() -> None:
    print("x1 x2 penalty")
    for first in (0, 1):
        for second in (0, 1):
            # ちょうど一方が1のときだけ、違反を表す罰点が0になる。
            print(first, second, penalty(first, second))


if __name__ == "__main__":
    main()
