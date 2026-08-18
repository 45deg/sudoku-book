from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Vector = NDArray[np.float64]


# BEGIN article-small-projections
def project_x_axis(point: Vector) -> Vector:
    """点をx軸上の最も近い位置へ移す。"""
    return np.array([point[0], 0.0])


def project_diagonal(point: Vector) -> Vector:
    """点を直線y=x上の最も近い位置へ移す。"""
    mean = (point[0] + point[1]) / 2.0
    return np.array([mean, mean])
# END article-small-projections


def main() -> None:
    point = np.array([2.0, 1.0])
    print(f"start: ({point[0]:.6f}, {point[1]:.6f})")
    # BEGIN article-alternating-projection
    for iteration in range(1, 6):
        # 二つの集合へ順番に射影し、共通部分である原点へ近づける。
        point = project_diagonal(project_x_axis(point))
        print(f"iteration {iteration}: ({point[0]:.6f}, {point[1]:.6f})")
    # END article-alternating-projection


if __name__ == "__main__":
    main()
