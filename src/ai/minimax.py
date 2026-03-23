from __future__ import annotations

from dataclasses import dataclass
from math import inf

from ai.heuristics import evaluate_state
from game.rules import apply_move, legal_moves
from game.state import GameState, Move


@dataclass(slots=True)
class SearchStats:
    nodes: int = 0
    prunes: int = 0


def choose_best_move(state: GameState, player: int, depth: int = 4) -> tuple[Move, SearchStats]:
    moves = legal_moves(state, player)
    if len(moves) == 1:
        return moves[0], SearchStats(nodes=1, prunes=0)

    alpha = -inf
    beta = inf
    best_value = -inf
    best_move = moves[0]
    stats = SearchStats()

    ordered_moves = sorted(moves, key=lambda m: 1 if m.is_pass else 0)
    for move in ordered_moves:
        child_state = apply_move(state, move)
        value = _minimax(
            state=child_state,
            depth=depth - 1,
            alpha=alpha,
            beta=beta,
            maximizing=False,
            perspective_player=player,
            stats=stats,
        )
        if value > best_value:
            best_value = value
            best_move = move
        alpha = max(alpha, best_value)

    return best_move, stats


def _minimax(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    perspective_player: int,
    stats: SearchStats,
) -> float:
    stats.nodes += 1

    if depth == 0 or state.round_over:
        return evaluate_state(state, perspective_player)

    current_player = state.current_player
    moves = legal_moves(state, current_player)
    ordered_moves = sorted(moves, key=lambda m: 1 if m.is_pass else 0)

    if maximizing:
        value = -inf
        for move in ordered_moves:
            child = apply_move(state, move)
            value = max(
                value,
                _minimax(
                    child,
                    depth - 1,
                    alpha,
                    beta,
                    maximizing=False,
                    perspective_player=perspective_player,
                    stats=stats,
                ),
            )
            alpha = max(alpha, value)
            if beta <= alpha:
                stats.prunes += 1
                break
        return value

    value = inf
    for move in ordered_moves:
        child = apply_move(state, move)
        value = min(
            value,
            _minimax(
                child,
                depth - 1,
                alpha,
                beta,
                maximizing=True,
                perspective_player=perspective_player,
                stats=stats,
            ),
        )
        beta = min(beta, value)
        if beta <= alpha:
            stats.prunes += 1
            break
    return value
