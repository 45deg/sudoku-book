% 数独の初期配置を、行・列・数字の事実として表します。
given(1, 1, 5).
given(1, 4, 6).

% 同じ行の別のマスには、すでに置かれた数字を使えません。
blocked_in_row(Row, Col, Digit) :-
    given(Row, OtherCol, Digit),
    between(1, 9, Col),
    Col \= OtherCol.
