from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.players import AlphaBetaAgent, GreedyAgent, RandomAgent
from game.engine import create_initial_state, play_match
from game.rules import apply_move, legal_moves
from game.state import GameState, Move, hand_points


def main() -> None:
    parser = argparse.ArgumentParser(description="Dominó IA - Prototipo académico")
    parser.add_argument("--mode", choices=["ai-vs-ai", "human-vs-ai"], default="ai-vs-ai")
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ai", choices=["alpha", "greedy", "random"], default="alpha")
    args = parser.parse_args()

    if args.mode == "ai-vs-ai":
        agent0 = AlphaBetaAgent(depth=args.depth)
        agent1 = GreedyAgent()
        result = play_match(agent0, agent1, seed=args.seed)
        print_summary(result)
        return

    run_human_vs_ai(args.ai, args.depth, args.seed)


def run_human_vs_ai(ai_type: str, depth: int, seed: int | None) -> None:
    ai_agent = _make_agent(ai_type, depth)
    human_index = 0
    state = create_initial_state(seed=seed)
    turn = 1

    print("=== Dominó (Humano vs IA) ===")
    while not state.round_over and turn <= 200:
        print(f"\nTurno {turn} - jugador actual: P{state.current_player}")
        print(f"Mesa: {_board_to_str(state)}")
        print(f"Puntos mano humana: {hand_points(state.hands[human_index])}")

        if state.current_player == human_index:
            move = _ask_human_move(state, human_index)
        else:
            move = ai_agent.choose_move(state, state.current_player)
            print(f"IA juega: {_move_to_str(move)}")

        state = apply_move(state, move)
        turn += 1

    print("\n=== Fin de partida ===")
    p0, p1 = hand_points(state.hands[0]), hand_points(state.hands[1])
    print(f"P0 puntos: {p0} | P1 puntos: {p1}")
    if state.winner is None:
        print("Empate")
    else:
        print(f"Ganador: P{state.winner}")


def _ask_human_move(state: GameState, player_index: int) -> Move:
    moves = legal_moves(state, player_index)
    print("Jugadas disponibles:")
    for idx, move in enumerate(moves):
        print(f"  [{idx}] {_move_to_str(move)}")

    while True:
        raw = input("Selecciona jugada por índice: ").strip()
        if not raw.isdigit():
            print("Entrada inválida. Ingresa un número.")
            continue
        selected = int(raw)
        if 0 <= selected < len(moves):
            return moves[selected]
        print("Índice fuera de rango.")


def _make_agent(ai_type: str, depth: int):
    if ai_type == "alpha":
        return AlphaBetaAgent(depth=depth)
    if ai_type == "greedy":
        return GreedyAgent()
    return RandomAgent()


def _board_to_str(state: GameState) -> str:
    return " ".join(str(t) for t in state.board) if state.board else "(vacía)"


def _move_to_str(move: Move) -> str:
    if move.is_pass:
        return "PASS"
    return f"{move.tile} -> {move.side}"


def print_summary(result) -> None:
    print("=== Resultado IA vs IA ===")
    print(f"Ganador: {result.winner}")
    print(f"Puntos P0: {result.p0_points} | Puntos P1: {result.p1_points}")
    print(f"Turnos: {result.turns}")
    print("-- Últimos 10 eventos --")
    for line in result.history[-10:]:
        print(line)


if __name__ == "__main__":
    main()
