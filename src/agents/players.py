from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from ai.heuristics import HeuristicName
from ai.minimax import SearchConfig, SearchStats, choose_best_move, choose_best_move_configured
from game.rules import apply_move, legal_moves
from game.state import GameState, Move, hand_points


class PlayerAgent(Protocol):
    name: str

    def choose_move(self, state: GameState, player_index: int) -> Move:
        ...


@dataclass(slots=True)
class RandomAgent:
    name: str = "random"

    def choose_move(self, state: GameState, player_index: int) -> Move:
        moves = legal_moves(state, player_index)
        return random.choice(moves)


@dataclass(slots=True)
class GreedyAgent:
    name: str = "greedy"

    def choose_move(self, state: GameState, player_index: int) -> Move:
        moves = legal_moves(state, player_index)
        if len(moves) == 1:
            return moves[0]

        best_move = moves[0]
        best_score = float("-inf")
        for move in moves:
            if move.is_pass:
                score = -10_000.0
            else:
                next_state = apply_move(state, move)
                my_points = hand_points(next_state.hands[player_index])
                score = -my_points
            if score > best_score:
                best_score = score
                best_move = move
        return best_move


@dataclass(slots=True)
class MinimaxAgent:
    depth: int = 4
    heuristic: HeuristicName = "linear"
    name: str = "minimax"
    last_stats: SearchStats | None = None

    def choose_move(self, state: GameState, player_index: int) -> Move:
        config = SearchConfig(depth=self.depth, heuristic=self.heuristic, use_alpha_beta=False)
        move, stats = choose_best_move_configured(state, player_index, config=config)
        self.last_stats = stats
        return move


@dataclass(slots=True)
class AlphaBetaAgent:
    depth: int = 4
    heuristic: HeuristicName = "legacy"
    name: str = "alpha_beta"
    last_stats: SearchStats | None = None

    def choose_move(self, state: GameState, player_index: int) -> Move:
        if self.heuristic == "legacy":
            move, stats = choose_best_move(state, player_index, depth=self.depth)
        else:
            config = SearchConfig(depth=self.depth, heuristic=self.heuristic, use_alpha_beta=True)
            move, stats = choose_best_move_configured(state, player_index, config=config)
        self.last_stats = stats
        return move
