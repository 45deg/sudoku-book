% BEGIN article-sudoku-rules
row(1..9).
column(1..9).
digit(1..9).

% 各マスについて、数字をちょうど一つ選びます。
1 { value(R, C, D) : digit(D) } 1 :- row(R), column(C).

% 同じ行や列で、同じ数字を二度使う割当を除きます。
:- value(R, C1, D), value(R, C2, D), C1 < C2.
:- value(R1, C, D), value(R2, C, D), R1 < R2.

% 行と列から3×3ブロックの番号を計算します。
block(R, C, B) :-
    row(R), column(C),
    B = ((R - 1) / 3) * 3 + ((C - 1) / 3) + 1.

% 同じブロックで、同じ数字を二度使う割当を除きます。
:- value(R1, C1, D), value(R2, C2, D),
   block(R1, C1, B), block(R2, C2, B),
   P1 = (R1 - 1) * 9 + C1, P2 = (R2 - 1) * 9 + C2, P1 < P2.

% 初期配置と異なる数字を選んだ割当を除きます。
:- given(R, C, D), not value(R, C, D).

#show value/3.
% END article-sudoku-rules

