#!/usr/bin/env python3
"""A two-item binary integer programming example."""

import highspy


# BEGIN article-small-example
model = highspy.Highs()
model.setOptionValue("output_flag", False)

# 品物を選ぶなら1、選ばないなら0になる二値変数です。
item_a = model.addBinary(name="item_a")
item_b = model.addBinary(name="item_b")

# 重さの合計を3以下にし、価値の合計を最大化します。
model.addConstr(2 * item_a + 3 * item_b <= 3)
model.maximize(3 * item_a + 4 * item_b)

status = model.getModelStatus()
print(f"status: {model.modelStatusToString(status)}")
print(f"item_a: {round(model.val(item_a))}")
print(f"item_b: {round(model.val(item_b))}")
print(f"objective: {model.getObjectiveValue():.0f}")
# END article-small-example
