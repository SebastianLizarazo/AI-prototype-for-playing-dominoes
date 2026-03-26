from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1] 
sys.path.insert(0, str(ROOT / "src")) # Agrega el directorio src al path para importar módulos

from agents.players import AlphaBetaAgent, GreedyAgent, RandomAgent
from game.engine import create_initial_state, play_match
from game.rules import apply_move, legal_moves
from game.state import GameState, Move, hand_points


def main() -> None:
    # Configuración de argumentos para el modo de juego
    parser = argparse.ArgumentParser(description="Dominó IA")
    parser.add_argument("--mode", choices=["ai-vs-ai", "human-vs-ai"], default="ai-vs-ai")
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--ai", choices=["alpha", "greedy", "random"], default="alpha")
    args = parser.parse_args()

    # Modo IA vs IA
    if args.mode == "ai-vs-ai":
        agent0 = AlphaBetaAgent(depth=args.depth)
        agent1 = GreedyAgent()
        result = play_match(agent0, agent1, seed=args.seed, collect_metrics=True)
        print_summary(result)
        return

    # Modo Humano vs IA
    run_human_vs_ai(args.ai, args.depth, args.seed) 


def run_human_vs_ai(ai_type: str, depth: int, seed: int | None) -> None:
    ai_agent = _make_agent(ai_type, depth)
    human_index = 0
    state = create_initial_state(seed=seed) # Seed es el estado inicial
    turn = 1

    print("Dominó modo Humano vs IA")
    # limitamos a 200 turnos para evitar loops infinitos en caso de error
    while not state.round_over and turn <= 200:
        print(f"\nTurno {turn} - jugador actual: Player {state.current_player}")
        print(f"Fichas en mesa: {_board_to_str(state)}")# fichas en la mesa
        print(f"Puntos mano humana: {hand_points(state.hands[human_index])}") 
        
        # Si es el turno del humano, le pedimos que elija una jugada. Si es el turno de la IA, ella elige su jugada automáticamente.
        if state.current_player == human_index:
            move = _ask_human_move(state, human_index)
        else:
            move = ai_agent.choose_move(state, state.current_player)
            print(f"IA juega: {_move_to_str(move)}")

        state = apply_move(state, move)
        turn += 1

    print("\n---Fin de partida---")
    p0, p1 = hand_points(state.hands[0]), hand_points(state.hands[1]) 
    print(f"Puntos Player0: {p0} | Puntos Player1: {p1}")
    if state.winner is None:
        print("Empate")
    else:
        print(f"Ganador: Player {state.winner}")

# Funciones auxiliares para manejar la interacción con el usuario y formatear la salida
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

# Crea el agente de IA según el tipo seleccionado
def _make_agent(ai_type: str, depth: int):
    if ai_type == "alpha": #
        return AlphaBetaAgent(depth=depth)
    if ai_type == "greedy": 
        return GreedyAgent()
    return RandomAgent()


def _board_to_str(state: GameState) -> str:
    return " ".join(str(t) for t in state.board) if state.board else "(vacía)" # Si no hay fichas en la mesa, mostramos "(vacía)"


def _move_to_str(move: Move) -> str:
    if move.is_pass:
        return "PASS"
    return f"{move.tile} -> {move.side}"


#
def print_summary(result) -> None:
    print("---Resultado IA vs IA ---")
    print(f"Ganador: Player{result.winner}")
    print(f"Puntos Player0: {result.p0_points} | Puntos Player1: {result.p1_points}")
    print(f"Turnos jugados: {result.turns}")
    print("--- Últimos 10 eventos ---")
    for line in result.history[-10:]:
        print(line)

    if result.move_metrics:
        p0 = [m for m in result.move_metrics if m.player == 0]
        p1 = [m for m in result.move_metrics if m.player == 1]
        print("--- Métricas de decisión ---")
        print(
            f"Player0 avg_ms={mean(m.elapsed_ms for m in p0):.3f} max_ms={max(m.elapsed_ms for m in p0):.3f} "
            f"avg_nodes={mean(m.nodes for m in p0):.2f} avg_prunes={mean(m.prunes for m in p0):.2f}"
        )
        print(
            f"Player1 avg_ms={mean(m.elapsed_ms for m in p1):.3f} max_ms={max(m.elapsed_ms for m in p1):.3f} "
            f"avg_nodes={mean(m.nodes for m in p1):.2f} avg_prunes={mean(m.prunes for m in p1):.2f}"
        )


if __name__ == "__main__":
    main()
