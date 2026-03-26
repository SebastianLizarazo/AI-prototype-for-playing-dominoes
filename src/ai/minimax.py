from __future__ import annotations

from dataclasses import dataclass
from math import inf

from ai.heuristics import HeuristicName, evaluate_state
from game.rules import apply_move, legal_moves
from game.state import GameState, Move

@dataclass(slots=True)
class SearchStats:
    nodes: int = 0
    prunes: int = 0


@dataclass(slots=True)
class SearchConfig:
    depth: int = 4
    heuristic: HeuristicName = "legacy"
    use_alpha_beta: bool = True


def choose_best_move(state: GameState, player: int, depth: int = 4) -> tuple[Move, SearchStats]:
    config = SearchConfig(depth=depth, heuristic="legacy", use_alpha_beta=True)
    return choose_best_move_configured(state, player, config)


def choose_best_move_configured(
    state: GameState,
    player: int,
    config: SearchConfig,
) -> tuple[Move, SearchStats]:
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
            depth=config.depth - 1,
            alpha=alpha,
            beta=beta,
            maximizing=False,
            perspective_player=player,
            stats=stats,
            heuristic=config.heuristic,
            use_alpha_beta=config.use_alpha_beta,
        )
        if value > best_value:
            best_value = value
            best_move = move
        if config.use_alpha_beta:
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
    heuristic: HeuristicName,
    use_alpha_beta: bool,
) -> float:
    stats.nodes += 1

    if depth == 0 or state.round_over:
        return evaluate_state(state, perspective_player, heuristic=heuristic)

    moves = legal_moves(state, state.current_player)
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
                    heuristic=heuristic,
                    use_alpha_beta=use_alpha_beta,
                ),
            )
            if use_alpha_beta:
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
                heuristic=heuristic,
                use_alpha_beta=use_alpha_beta,
            ),
        )
        if use_alpha_beta:
            beta = min(beta, value)
            if beta <= alpha:
                stats.prunes += 1
                break
    return value
