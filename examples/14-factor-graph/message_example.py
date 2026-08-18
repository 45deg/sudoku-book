#!/usr/bin/env python3
"""Compare sum-product and max-product messages for one factor."""

from __future__ import annotations

from solve import all_different_message


def show(values: tuple[float, ...] | None) -> str:
    if values is None:
        return "none"
    return "[" + ", ".join(f"{value:.3f}" for value in values) + "]"


def main() -> None:
    # xへのメッセージを求めるので、x自身から届いた値は計算に使われません。
    incoming = (
        (1 / 3, 1 / 3, 1 / 3),
        (0.6, 0.3, 0.1),
        (0.2, 0.3, 0.5),
    )
    print("sum-product:", show(all_different_message(incoming, 0, "sum-product")))
    print("max-product:", show(all_different_message(incoming, 0, "max-product")))


if __name__ == "__main__":
    main()
