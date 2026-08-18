from __future__ import annotations

from collections.abc import Iterable

from dd.autoref import BDD, Function


def decision_node_count(bdd: BDD, root: Function) -> int:
    """rootから到達できる非終端ノードの個数を返す。"""
    seen: set[int] = set()
    pending = [root]

    while pending:
        node = pending.pop()
        # ddは否定した枝を負の番号で表すため、絶対値で同じノードにまとめる。
        node_id = abs(node.node)
        if node_id in seen:
            continue
        _level, low, high = bdd.succ(node)
        if low is None or high is None:
            continue
        seen.add(node_id)
        pending.extend((low, high))

    return len(seen)


# BEGIN article-exactly-one
def exactly_one(bdd: BDD, names: Iterable[str]) -> Function:
    """列挙した変数のうち、ちょうど一つが真になるBDDを作る。"""
    variables = [bdd.var(name) for name in names]

    # 少なくとも一つを選ぶ条件を、論理和として作る。
    at_least_one = bdd.false
    for variable in variables:
        at_least_one |= variable

    # 二つを同時に選べない条件を、すべての組について加える。
    at_most_one = bdd.true
    for index, left in enumerate(variables):
        for right in variables[index + 1 :]:
            at_most_one &= ~left | ~right

    return at_least_one & at_most_one
# END article-exactly-one
