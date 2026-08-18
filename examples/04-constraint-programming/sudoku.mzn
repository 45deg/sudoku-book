include "alldifferent.mzn";

int: n;
int: box;
array[1..n, 1..n] of 0..n: givens;

% BEGIN article-model
% それぞれのマスを、1からnまでの値を取る有限領域変数にします。
array[1..n, 1..n] of var 1..n: cell;

% 初期配置があるマスは、その数字に固定します。
constraint forall (r, c in 1..n where givens[r, c] != 0) (
  cell[r, c] = givens[r, c]
);

% 行と列では、n個のマスがすべて異なる値を取ります。
constraint forall (r in 1..n) (
  all_different([cell[r, c] | c in 1..n])
);
constraint forall (c in 1..n) (
  all_different([cell[r, c] | r in 1..n])
);

% box×boxブロックも、同じall_different制約で表します。
constraint forall (br, bc in 0..box - 1) (
  all_different([
    cell[br * box + dr, bc * box + dc]
    | dr, dc in 1..box
  ])
);
% END article-model

% BEGIN article-search
% 候補数が最少のマスを選び、残った数字を小さい順に試します。
solve :: int_search(
  [cell[r, c] | r, c in 1..n],
  first_fail,
  indomain_min,
  complete
) satisfy;
% END article-search

% 一つの解を9行（または4行）の数字として出力します。
output [
  concat([show(cell[r, c]) | c in 1..n]) ++
  if r < n then "\n" else "" endif
  | r in 1..n
];
