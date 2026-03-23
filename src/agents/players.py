from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from ai.minimax import SearchStats, choose_best_move
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
class AlphaBetaAgent:
    depth: int = 4
    name: str = "alpha_beta"
    last_stats: SearchStats | None = None

    def choose_move(self, state: GameState, player_index: int) -> Move:
        move, stats = choose_best_move(state, player_index, depth=self.depth)
        self.last_stats = stats
        return move
