#!/usr/bin/env python3
"""A small integer-arithmetic example for the SMT article."""

from z3 import Ints, SolverFor, sat


# BEGIN article-small-example
x, y = Ints("x y")
solver = SolverFor("QF_LIA")

# 二つの整数を、連立方程式を満たす値に制約します。
solver.add(x + y == 7)
solver.add(x - y == 3)

result = solver.check()
print(f"status: {result}")
if result == sat:
    # 充足する値をモデルから整数として読み戻します。
    model = solver.model()
    print(f"x: {model.eval(x).as_long()}")
    print(f"y: {model.eval(y).as_long()}")
# END article-small-example
