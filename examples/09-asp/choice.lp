% 選べる飲み物を事実として並べます。
option(tea; coffee; water).

% 三つの候補から、ちょうど一つを選びます。
1 { drink(X) : option(X) } 1.

% coffeeを含む候補は、安定モデルとして認めません。
:- drink(coffee).

#show drink/1.

