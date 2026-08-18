:- module(sudoku_prolog, [solve_numbers/3, main/0]).

% This solver is designed specifically for standard 9x9 Sudoku grids.

:- use_module(library(readutil)).
:- use_module(library(solution_sequences)).

:- initialization(main, main).

% BEGIN article-board
numbers_cells([], []).
numbers_cells([0|Numbers], [_|Cells]) :-
    % 0のマスには、新しい論理変数を一つ置きます。
    numbers_cells(Numbers, Cells).
numbers_cells([Number|Numbers], [Number|Cells]) :-
    Number \= 0,
    % 初期配置の数字は、整数のまま盤面に残します。
    numbers_cells(Numbers, Cells).
% END article-board

solve_numbers(Numbers, Limit, Solutions) :-
    must_be(integer, Limit),
    Limit > 0,
    valid_numbers(Numbers),
    numbers_cells(Numbers, Cells),
    (   consistent_cells(Cells)
    ->  once(findnsols(Limit, Cells, search(Cells), Solutions))
    ;   % 初期配置がすでに重複している場合も、解なしとして扱います。
        Solutions = []
    ).

% BEGIN article-search
search(Cells) :-
    (   has_variable(Cells)
    ->  best_cell(Cells, Cell, Candidates),
        % 候補が空ならここで失敗し、Prologが直前の選択肢へ戻ります。
        Candidates \= [],
        member(Value, Candidates),
        % 単一化によって、選んだ数字を論理変数へ仮置きします。
        Cell = Value,
        search(Cells)
    ;   % 論理変数が残っていなければ、盤面は完成しています。
        true
    ).

has_variable([Cell|_]) :-
    var(Cell),
    !.
has_variable([_|Cells]) :-
    has_variable(Cells).

best_cell(Cells, Cell, Candidates) :-
    findall(
        Count-(Index-CellCandidates),
        (   nth0(Index, Cells, Current),
            var(Current),
            candidate_digits(Cells, Index, CellCandidates),
            length(CellCandidates, Count)
        ),
        Choices
    ),
    % 候補数をキーに並べ、分岐の少ないマスを選びます。
    keysort(Choices, [_-(Index-Candidates)|_]),
    nth0(Index, Cells, Cell).

candidate_digits(Cells, Index, Candidates) :-
    used_values(Cells, Index, Used),
    findall(
        Digit,
        (between(1, 9, Digit), \+ memberchk(Digit, Used)),
        Candidates
    ).
% END article-search

used_values(Cells, Index, Used) :-
    Row is Index // 9,
    Col is Index mod 9,
    BoxRow is (Row // 3) * 3,
    BoxCol is (Col // 3) * 3,
    row_values(Cells, Row, RowValues),
    column_values(Cells, Col, ColValues),
    box_values(Cells, BoxRow, BoxCol, BoxValues),
    append([RowValues, ColValues, BoxValues], Values),
    include(integer, Values, GroundValues),
    sort(GroundValues, Used).

row_values(Cells, Row, Values) :-
    Start is Row * 9,
    findall(Value, (between(0, 8, Offset), Index is Start + Offset,
                    nth0(Index, Cells, Value)), Values).

column_values(Cells, Col, Values) :-
    findall(Value, (between(0, 8, Row), Index is Row * 9 + Col,
                    nth0(Index, Cells, Value)), Values).

box_values(Cells, BoxRow, BoxCol, Values) :-
    findall(
        Value,
        (   between(0, 2, RowOffset),
            between(0, 2, ColOffset),
            Row is BoxRow + RowOffset,
            Col is BoxCol + ColOffset,
            Index is Row * 9 + Col,
            nth0(Index, Cells, Value)
        ),
        Values
    ).

consistent_cells(Cells) :-
    forall(between(0, 8, Row),
           (row_values(Cells, Row, Values), no_duplicate_numbers(Values))),
    forall(between(0, 8, Col),
           (column_values(Cells, Col, Values), no_duplicate_numbers(Values))),
    forall(
        (between(0, 2, BoxRowIndex), between(0, 2, BoxColIndex)),
        (   BoxRow is BoxRowIndex * 3,
            BoxCol is BoxColIndex * 3,
            box_values(Cells, BoxRow, BoxCol, Values),
            no_duplicate_numbers(Values)
        )
    ).

no_duplicate_numbers(Values) :-
    include(integer, Values, Numbers),
    sort(Numbers, Unique),
    length(Numbers, Count),
    length(Unique, Count).

valid_numbers(Numbers) :-
    length(Numbers, 81),
    maplist(valid_number, Numbers).

valid_number(Number) :-
    integer(Number),
    between(0, 9, Number).

read_numbers(Path, Numbers) :-
    read_file_to_codes(Path, Codes, []),
    board_codes(Codes, Numbers),
    valid_numbers(Numbers).

board_codes([], []).
board_codes([Code|Codes], Numbers) :-
    (   code_type(Code, digit)
    ->  Number is Code - 0'0,
        Numbers = [Number|Rest]
    ;   Code =:= 0'.
    ->  Numbers = [0|Rest]
    ;   code_type(Code, space)
    ->  Numbers = Rest
    ;   throw(error(domain_error(board_character, Code), _))
    ),
    board_codes(Codes, Rest).

main :-
    current_prolog_flag(argv, Argv),
    catch(run(Argv), Error, (print_message(error, Error), halt(2))),
    halt.

run(Argv) :-
    parse_arguments(Argv, Path, Limit),
    read_numbers(Path, Numbers),
    solve_numbers(Numbers, Limit, Solutions),
    print_result(Limit, Solutions).

parse_arguments([Path], Path, 1).
parse_arguments([Path, '--limit', LimitAtom], Path, Limit) :-
    atom_number(LimitAtom, Limit),
    integer(Limit),
    Limit > 0.
parse_arguments(_, _, _) :-
    throw(error(domain_error(arguments,
        'solve.pl BOARD [--limit POSITIVE_INTEGER]'), _)).

print_result(Limit, Solutions) :-
    length(Solutions, Count),
    format('engine: SWI-Prolog without CLP(FD)~n'),
    format('limit: ~d~n', [Limit]),
    format('solutions: ~d~n', [Count]),
    print_status(Count),
    print_search_complete(Count, Limit),
    print_uniqueness(Count, Limit),
    print_solutions(Solutions, 1).

print_status(0) :-
    writeln('status: unsat').
print_status(Count) :-
    Count > 0,
    writeln('status: solved').

print_search_complete(Count, Limit) :-
    (   Count < Limit
    ->  writeln('search complete: yes')
    ;   writeln('search complete: no')
    ).

print_uniqueness(0, _) :-
    writeln('uniqueness: not applicable').
print_uniqueness(1, Limit) :-
    Limit > 1,
    writeln('uniqueness: unique').
print_uniqueness(1, 1) :-
    writeln('uniqueness: not checked').
print_uniqueness(Count, _) :-
    Count >= 2,
    writeln('uniqueness: not unique').

print_solutions([], _).
print_solutions([Solution|Solutions], Number) :-
    format('solution ~d:~n', [Number]),
    print_board(Solution),
    Next is Number + 1,
    print_solutions(Solutions, Next).

print_board([]).
print_board(Cells) :-
    length(Row, 9),
    append(Row, Rest, Cells),
    atomic_list_concat(Row, '', Line),
    writeln(Line),
    print_board(Rest).
