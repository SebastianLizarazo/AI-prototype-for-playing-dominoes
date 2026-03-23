from __future__ import annotations

import random
from dataclasses import dataclass

from agents.players import PlayerAgent
from game.domino import Tile, generate_double_six_set
from game.rules import apply_move, legal_moves
from game.state import GameState, Move, hand_points


@dataclass(slots=True)
class MatchResult:
    winner: int | None
    p0_points: int
    p1_points: int
    turns: int
    history: list[str]


def create_initial_state(seed: int | None = None) -> GameState:
    rng = random.Random(seed)
    tiles = generate_double_six_set()
    rng.shuffle(tiles)

    hand0 = tuple(tiles[:7])
    hand1 = tuple(tiles[7:14])
    return GameState(board=tuple(), hands=(hand0, hand1), current_player=0)


def play_match(agent0: PlayerAgent, agent1: PlayerAgent, seed: int | None = None, max_turns: int = 200) -> MatchResult:
    state = create_initial_state(seed=seed)
    history: list[str] = []

    for turn in range(1, max_turns + 1):
        if state.round_over:
            break

        current_player = state.current_player
        agent = agent0 if current_player == 0 else agent1
        move = agent.choose_move(state, current_player)
        _validate_agent_move(state, current_player, move)
        history.append(_format_turn(turn, current_player, agent.name, move, state.board))
        state = apply_move(state, move)

    p0_points = hand_points(state.hands[0])
    p1_points = hand_points(state.hands[1])
    winner = state.winner
    if winner is None and state.round_over:
        if p0_points < p1_points:
            winner = 0
        elif p1_points < p0_points:
            winner = 1

    return MatchResult(
        winner=winner,
        p0_points=p0_points,
        p1_points=p1_points,
        turns=len(history),
        history=history,
    )


def _validate_agent_move(state: GameState, player: int, move: Move) -> None:
    valid = legal_moves(state, player)
    if move not in valid:
        raise ValueError(f"Illegal move from player {player}: {move}")


def _format_turn(turn: int, player: int, agent_name: str, move: Move, board: tuple[Tile, ...]) -> str:
    board_str = " ".join(str(t) for t in board) if board else "(empty)"
    if move.is_pass:
        action = "PASS"
    else:
        action = f"{move.tile} -> {move.side}"
    return f"T{turn:03d} P{player}({agent_name}) {action} | board: {board_str}"
