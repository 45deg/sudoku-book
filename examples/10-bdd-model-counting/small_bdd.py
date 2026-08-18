from __future__ import annotations

from dd.autoref import BDD, Function

from bdd_utils import decision_node_count


# BEGIN article-small-bdd
def build_mux(order: tuple[str, ...]) -> tuple[BDD, Function]:
    bdd = BDD()
    bdd.declare(*order)
    x, y, z = (bdd.var(name) for name in ("x", "y", "z"))

    # xが真ならy、偽ならzを採用する論理式をBDDへ変換する。
    formula = (x & y) | (~x & z)
    return bdd, formula
# END article-small-bdd


def main() -> None:
    for order in (("x", "y", "z"), ("y", "z", "x")):
        bdd, formula = build_mux(order)
        models = list(bdd.pick_iter(formula, care_vars={"x", "y", "z"}))
        print(f"order: {','.join(order)}")
        print(f"decision_nodes: {decision_node_count(bdd, formula)}")
        print(f"models: {len(models)}")


if __name__ == "__main__":
    main()
