from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean, stdev


@dataclass(slots=True)
class DistributionSummary:
    mean: float
    std: float
    ci95_low: float
    ci95_high: float


@dataclass(slots=True)
class StrategyAggregate:
    strategy: str
    matches: int
    wins: int
    losses: int
    draws: int
    win_rate: float
    avg_turns: float
    std_turns: float
    avg_point_diff: float
    std_point_diff: float
    avg_nodes: float
    std_nodes: float
    avg_prunes: float
    std_prunes: float
    avg_decision_ms: float
    std_decision_ms: float
    max_latency_ms: float
    avg_cpu_ms: float
    std_cpu_ms: float
    turns_ci95_low: float
    turns_ci95_high: float
    point_diff_ci95_low: float
    point_diff_ci95_high: float



def summarize_distribution(values: list[float]) -> DistributionSummary:
    if not values:
        return DistributionSummary(mean=0.0, std=0.0, ci95_low=0.0, ci95_high=0.0)

    sample_mean = mean(values)
    if len(values) == 1:
        return DistributionSummary(mean=sample_mean, std=0.0, ci95_low=sample_mean, ci95_high=sample_mean)

    sample_std = stdev(values)
    margin = 1.96 * (sample_std / sqrt(len(values)))
    return DistributionSummary(
        mean=sample_mean,
        std=sample_std,
        ci95_low=sample_mean - margin,
        ci95_high=sample_mean + margin,
    )


def aggregate_strategy_results(strategy: str, match_rows: list[dict], move_rows: list[dict]) -> StrategyAggregate:
    wins = sum(1 for row in match_rows if row["outcome"] == "win")
    losses = sum(1 for row in match_rows if row["outcome"] == "loss")
    draws = sum(1 for row in match_rows if row["outcome"] == "draw")

    turns_values = [float(row["turns"]) for row in match_rows]
    point_diff_values = [float(row["point_diff"]) for row in match_rows]
    nodes_values = [float(row["avg_nodes"]) for row in match_rows]
    prunes_values = [float(row["avg_prunes"]) for row in match_rows]
    decision_ms_values = [float(row["avg_decision_ms"]) for row in match_rows]
    cpu_ms_values = [float(row["avg_cpu_ms"]) for row in match_rows]
    latency_values = [float(row["max_latency_ms"]) for row in match_rows]

    turns_summary = summarize_distribution(turns_values)
    point_summary = summarize_distribution(point_diff_values)
    nodes_summary = summarize_distribution(nodes_values)
    prunes_summary = summarize_distribution(prunes_values)
    decision_summary = summarize_distribution(decision_ms_values)
    cpu_summary = summarize_distribution(cpu_ms_values)

    total_matches = len(match_rows)
    win_rate = (wins / total_matches) if total_matches else 0.0

    return StrategyAggregate(
        strategy=strategy,
        matches=total_matches,
        wins=wins,
        losses=losses,
        draws=draws,
        win_rate=win_rate,
        avg_turns=turns_summary.mean,
        std_turns=turns_summary.std,
        avg_point_diff=point_summary.mean,
        std_point_diff=point_summary.std,
        avg_nodes=nodes_summary.mean,
        std_nodes=nodes_summary.std,
        avg_prunes=prunes_summary.mean,
        std_prunes=prunes_summary.std,
        avg_decision_ms=decision_summary.mean,
        std_decision_ms=decision_summary.std,
        max_latency_ms=max(latency_values) if latency_values else 0.0,
        avg_cpu_ms=cpu_summary.mean,
        std_cpu_ms=cpu_summary.std,
        turns_ci95_low=turns_summary.ci95_low,
        turns_ci95_high=turns_summary.ci95_high,
        point_diff_ci95_low=point_summary.ci95_low,
        point_diff_ci95_high=point_summary.ci95_high,
    )
