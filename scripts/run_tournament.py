from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.players import AlphaBetaAgent, GreedyAgent, RandomAgent
from game.engine import play_match


def main() -> None:
    parser = argparse.ArgumentParser(description="Torneo rápido de agentes Dominó")
    parser.add_argument("--matches", type=int, default=50)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--opponent", choices=["greedy", "random"], default="greedy")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    wins = 0
    draws = 0
    total_turns = 0

    # Ejecuta el torneo entre el agente AlphaBeta y el oponente seleccionado (Greedy o Random)
    for i in range(args.matches):
        agent0 = AlphaBetaAgent(depth=args.depth)
        agent1 = GreedyAgent() if args.opponent == "greedy" else RandomAgent()
        result = play_match(agent0, agent1, seed=args.seed + i)
        total_turns += result.turns
        if result.winner == 0:
            wins += 1
        elif result.winner is None:
            draws += 1

    print("---Torneo---")
    print(f"Partidas: {args.matches}")
    print(f"Wins IA(AlphaBeta): {wins}")
    print(f"Draws: {draws}")
    print(f"Losses: {args.matches - wins - draws}")
    print(f"Win rate: {wins / args.matches:.2%}")
    print(f"Turnos promedio: {total_turns / args.matches:.2f}")


if __name__ == "__main__":
    main()
