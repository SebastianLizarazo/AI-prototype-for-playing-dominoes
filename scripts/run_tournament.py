from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agents.players import AlphaBetaAgent, GreedyAgent, MinimaxAgent, RandomAgent
from ai.heuristics import HeuristicName
from benchmarking.analytics import StrategyAggregate, aggregate_strategy_results
from game.engine import play_match


@dataclass(slots=True)
class StrategyConfig:
    name: str
    algorithm: str
    heuristic: HeuristicName
    depth: int


MATCHES_COLUMN_MAP = {
    "strategy": "Strategy",
    "algorithm": "Search Algorithm",
    "heuristic": "Heuristic",
    "depth": "Search Depth",
    "base_seed": "Base Seed",
    "match_index": "Match ID",
    "seat": "Seat",
    "opponent": "Opponent Policy",
    "turns": "Turns",
    "winner": "Winner Player",
    "outcome": "Outcome",
    "point_diff": "Point Difference",
    "avg_nodes": "Avg Nodes per Decision",
    "avg_prunes": "Avg Prunes per Decision",
    "avg_decision_ms": "Avg Decision Time (ms)",
    "avg_cpu_ms": "Avg CPU Time (ms)",
    "max_latency_ms": "Max Decision Time (ms)",
}

MOVES_COLUMN_MAP = {
    "strategy": "Strategy",
    "algorithm": "Search Algorithm",
    "heuristic": "Heuristic",
    "depth": "Search Depth",
    "base_seed": "Base Seed",
    "match_index": "Match ID",
    "seat": "Seat",
    "turn": "Turn",
    "elapsed_ms": "Decision Time (ms)",
    "cpu_ms": "CPU Time (ms)",
    "nodes": "Nodes Expanded",
    "prunes": "Nodes Pruned",
    "is_pass": "Is Pass",
}

SUMMARY_COLUMN_MAP = {
    "strategy": "Strategy",
    "matches": "Matches",
    "wins": "Wins",
    "losses": "Losses",
    "draws": "Draws",
    "win_rate": "Win Rate",
    "avg_turns": "Avg Turns",
    "std_turns": "Std Turns",
    "avg_point_diff": "Avg Point Difference",
    "std_point_diff": "Std Point Difference",
    "avg_nodes": "Avg Nodes per Decision",
    "std_nodes": "Std Nodes per Decision",
    "avg_prunes": "Avg Prunes per Decision",
    "std_prunes": "Std Prunes per Decision",
    "avg_decision_ms": "Avg Decision Time (ms)",
    "std_decision_ms": "Std Decision Time (ms)",
    "max_latency_ms": "Max Decision Time (ms)",
    "avg_cpu_ms": "Avg CPU Time (ms)",
    "std_cpu_ms": "Std CPU Time (ms)",
    "turns_ci95_low": "Turns CI95 Low",
    "turns_ci95_high": "Turns CI95 High",
    "point_diff_ci95_low": "Point Diff CI95 Low",
    "point_diff_ci95_high": "Point Diff CI95 High",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark reproducible de agentes Dominó")
    parser.add_argument("--matches", type=int, default=30)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--opponent", choices=["greedy", "random", "alpha"], default="greedy")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--swap-seats", dest="swap_seats", action="store_true")
    parser.add_argument("--no-swap-seats", dest="swap_seats", action="store_false")
    parser.set_defaults(swap_seats=True)
    parser.add_argument("--out", type=str, default="results")
    args = parser.parse_args()

    output_dir = ROOT / args.out
    output_dir.mkdir(parents=True, exist_ok=True)

    base_seeds = [args.seed + i for i in range(args.matches)]
    strategy_configs = _build_strategy_grid(depth=args.depth)

    all_match_rows: list[dict] = []
    all_move_rows: list[dict] = []
    aggregates: list[StrategyAggregate] = []

    for strategy in strategy_configs:
        strategy_match_rows: list[dict] = []
        strategy_move_rows: list[dict] = []

        for match_index, seed in enumerate(base_seeds):
            seat_orders = [0, 1] if args.swap_seats else [0]
            for seat in seat_orders:
                strategy_player = seat
                opponent_player = 1 - strategy_player

                strat_agent = _make_strategy_agent(strategy)
                opp_agent = _make_opponent(args.opponent, args.depth)
                if strategy_player == 0:
                    agent0, agent1 = strat_agent, opp_agent
                else:
                    agent0, agent1 = opp_agent, strat_agent

                result = play_match(agent0, agent1, seed=seed, collect_metrics=True)

                strategy_moves = [metric for metric in result.move_metrics if metric.player == strategy_player]
                avg_nodes = _safe_avg([metric.nodes for metric in strategy_moves])
                avg_prunes = _safe_avg([metric.prunes for metric in strategy_moves])
                avg_ms = _safe_avg([metric.elapsed_ms for metric in strategy_moves])
                avg_cpu_ms = _safe_avg([metric.cpu_ms for metric in strategy_moves])
                max_latency = max((metric.elapsed_ms for metric in strategy_moves), default=0.0)

                p_strategy = result.p0_points if strategy_player == 0 else result.p1_points
                p_opponent = result.p1_points if strategy_player == 0 else result.p0_points
                point_diff = p_opponent - p_strategy

                if result.winner is None:
                    outcome = "draw"
                elif result.winner == strategy_player:
                    outcome = "win"
                else:
                    outcome = "loss"

                row = {
                    "strategy": strategy.name,
                    "algorithm": strategy.algorithm,
                    "heuristic": strategy.heuristic,
                    "depth": strategy.depth,
                    "base_seed": seed,
                    "match_index": match_index,
                    "seat": strategy_player,
                    "opponent": args.opponent,
                    "turns": result.turns,
                    "winner": result.winner,
                    "outcome": outcome,
                    "point_diff": point_diff,
                    "avg_nodes": avg_nodes,
                    "avg_prunes": avg_prunes,
                    "avg_decision_ms": avg_ms,
                    "avg_cpu_ms": avg_cpu_ms,
                    "max_latency_ms": max_latency,
                }
                strategy_match_rows.append(row)
                all_match_rows.append(row)

                for metric in strategy_moves:
                    move_row = {
                        "strategy": strategy.name,
                        "algorithm": strategy.algorithm,
                        "heuristic": strategy.heuristic,
                        "depth": strategy.depth,
                        "base_seed": seed,
                        "match_index": match_index,
                        "seat": strategy_player,
                        "turn": metric.turn,
                        "elapsed_ms": metric.elapsed_ms,
                        "cpu_ms": metric.cpu_ms,
                        "nodes": metric.nodes,
                        "prunes": metric.prunes,
                        "is_pass": metric.is_pass,
                    }
                    strategy_move_rows.append(move_row)
                    all_move_rows.append(move_row)

        aggregate = aggregate_strategy_results(strategy.name, strategy_match_rows, strategy_move_rows)
        aggregates.append(aggregate)

    summary_rows = [asdict(aggregate) for aggregate in aggregates]
    _export_csv(output_dir / "benchmark_matches.csv", all_match_rows, MATCHES_COLUMN_MAP)
    _export_csv(output_dir / "benchmark_moves.csv", all_move_rows, MOVES_COLUMN_MAP)
    _export_csv(output_dir / "benchmark_summary.csv", summary_rows, SUMMARY_COLUMN_MAP)
    _export_json(output_dir / "benchmark_report.json", {
        "config": {
            "matches": args.matches,
            "depth": args.depth,
            "seed": args.seed,
            "swap_seats": args.swap_seats,
            "opponent": args.opponent,
            "base_seeds": base_seeds,
        },
        "summary": summary_rows,
    })

    print("--- Benchmark reproducible ---")
    print(f"Partidas base por estrategia: {args.matches} | swap_seats={args.swap_seats}")
    print(f"Semillas compartidas: {base_seeds[:5]}{' ...' if len(base_seeds) > 5 else ''}")
    print("\nEstrategia                                win_rate  avg_turns  avg_nodes  avg_prunes  avg_ms  max_ms")
    for aggregate in sorted(aggregates, key=lambda item: item.win_rate, reverse=True):
        print(
            f"{aggregate.strategy:<40} {aggregate.win_rate:>8.2%}"
            f" {aggregate.avg_turns:>10.2f} {aggregate.avg_nodes:>10.2f}"
            f" {aggregate.avg_prunes:>11.2f} {aggregate.avg_decision_ms:>7.3f} {aggregate.max_latency_ms:>7.3f}"
        )

    print("\nArchivos exportados:")
    print(f"- {output_dir / 'benchmark_matches.csv'}")
    print(f"- {output_dir / 'benchmark_moves.csv'}")
    print(f"- {output_dir / 'benchmark_summary.csv'}")
    print(f"- {output_dir / 'benchmark_report.json'}")


def _build_strategy_grid(depth: int) -> list[StrategyConfig]:
    heuristics: list[HeuristicName] = ["linear", "manhattan", "euclidean"]
    strategies: list[StrategyConfig] = []
    for heuristic in heuristics:
        strategies.append(
            StrategyConfig(
                name=f"alpha_beta::{heuristic}",
                algorithm="alpha_beta",
                heuristic=heuristic,
                depth=depth,
            )
        )
        strategies.append(
            StrategyConfig(
                name=f"minimax::{heuristic}",
                algorithm="minimax",
                heuristic=heuristic,
                depth=depth,
            )
        )
    return strategies


def _make_strategy_agent(config: StrategyConfig):
    if config.algorithm == "alpha_beta":
        return AlphaBetaAgent(depth=config.depth, heuristic=config.heuristic, name=config.name)
    return MinimaxAgent(depth=config.depth, heuristic=config.heuristic, name=config.name)


def _make_opponent(name: str, depth: int):
    if name == "greedy":
        return GreedyAgent()
    if name == "random":
        return RandomAgent()
    return AlphaBetaAgent(depth=depth, heuristic="legacy", name="alpha_beta_legacy")


def _safe_avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _export_csv(path: Path, rows: list[dict], column_map: dict[str, str]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    ordered_keys = [key for key in column_map if key in rows[0]]
    fieldnames = [column_map[key] for key in ordered_keys]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(_format_csv_row(row, ordered_keys, column_map))


def _format_csv_row(row: dict, ordered_keys: list[str], column_map: dict[str, str]) -> dict:
    formatted_row: dict = {}
    for key in ordered_keys:
        value = row.get(key)
        if key == "strategy" and isinstance(value, str):
            value = _latex_safe_strategy(value)
        elif key == "algorithm" and isinstance(value, str):
            value = _human_algorithm_name(value)
        elif key == "heuristic" and isinstance(value, str):
            value = value.title()

        if isinstance(value, float):
            value = round(value, 3)

        formatted_row[column_map[key]] = value
    return formatted_row


def _latex_safe_strategy(strategy_name: str) -> str:
    if "::" in strategy_name:
        algorithm, heuristic = strategy_name.split("::", maxsplit=1)
        human_algorithm = _human_algorithm_name(algorithm)
        human_heuristic = heuristic.title()
        return f"{human_algorithm} ({human_heuristic})"
    return strategy_name.replace("_", r"\_")


def _human_algorithm_name(algorithm: str) -> str:
    normalized = algorithm.strip().lower()
    if normalized == "alpha_beta":
        return "Alpha-Beta"
    if normalized == "minimax":
        return "Minimax"
    return algorithm.replace("_", " ").title()


def _export_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
