from __future__ import annotations

from math import sqrt
from typing import Literal

from game.rules import legal_moves
from game.state import GameState, hand_points


HeuristicName = Literal["legacy", "linear", "manhattan", "euclidean"]

def evaluate_state(state: GameState, perspective_player: int, heuristic: HeuristicName = "legacy") -> float:
    if state.round_over:
        return _terminal_utility(state, perspective_player)

    if heuristic == "legacy":
        return _legacy_evaluation(state, perspective_player)

    distance = _distance_score(state, perspective_player, heuristic)
    return distance_to_utility(distance)


def distance_to_utility(distance: float) -> float:
    return -distance


def _terminal_utility(state: GameState, perspective_player: int) -> float:
    if state.winner is None:
        return hand_points(state.hands[1 - perspective_player]) - hand_points(state.hands[perspective_player])
    return 10_000.0 if state.winner == perspective_player else -10_000.0


def _legacy_evaluation(state: GameState, perspective_player: int) -> float:
    my_hand = state.hands[perspective_player]
    opp_hand = state.hands[1 - perspective_player]

    my_count = len(my_hand)
    opp_count = len(opp_hand)
    score = (opp_count - my_count) * 25.0

    my_points = hand_points(my_hand)
    opp_points = hand_points(opp_hand)
    score += (opp_points - my_points) * 2.0

    my_mobility = len(legal_moves(state, perspective_player))
    opp_mobility = len(legal_moves(state, 1 - perspective_player))
    score += (my_mobility - opp_mobility) * 8.0

    left_end = state.left_end
    right_end = state.right_end
    if left_end is not None and right_end is not None:
        my_control = sum(1 for t in my_hand if t.left in (left_end, right_end) or t.right in (left_end, right_end))
        opp_control = sum(1 for t in opp_hand if t.left in (left_end, right_end) or t.right in (left_end, right_end))
        score += (my_control - opp_control) * 3.0

    my_unique_values = len({value for tile in my_hand for value in (tile.left, tile.right)})
    score += my_unique_values * 1.5
    return score


def _distance_score(state: GameState, perspective_player: int, heuristic: HeuristicName) -> float:
    if heuristic == "manhattan":
        return _manhattan_distance(state, perspective_player)
    if heuristic == "euclidean":
        return _euclidean_distance(state, perspective_player)
    return _linear_distance(state, perspective_player)


def _relative_features(state: GameState, perspective_player: int) -> tuple[float, float, float, float]:
    my_hand = state.hands[perspective_player]
    opp_hand = state.hands[1 - perspective_player]

    my_count = len(my_hand)
    opp_count = len(opp_hand)
    my_points = hand_points(my_hand)
    opp_points = hand_points(opp_hand)
    my_mobility = len(legal_moves(state, perspective_player))
    opp_mobility = len(legal_moves(state, 1 - perspective_player))

    count_delta = float(my_count - opp_count)
    points_delta = float(my_points - opp_points)
    mobility_delta = float(opp_mobility - my_mobility)

    left_end = state.left_end
    right_end = state.right_end
    if left_end is None or right_end is None:
        control_delta = 0.0
    else:
        my_control = sum(1 for t in my_hand if t.left in (left_end, right_end) or t.right in (left_end, right_end))
        opp_control = sum(1 for t in opp_hand if t.left in (left_end, right_end) or t.right in (left_end, right_end))
        control_delta = float(opp_control - my_control)

    return count_delta, points_delta, mobility_delta, control_delta


def _linear_distance(state: GameState, perspective_player: int) -> float:
    count_delta, points_delta, mobility_delta, control_delta = _relative_features(state, perspective_player)
    return 25.0 * count_delta + 2.0 * points_delta + 8.0 * mobility_delta + 3.0 * control_delta


def _manhattan_distance(state: GameState, perspective_player: int) -> float:
    count_delta, points_delta, mobility_delta, control_delta = _relative_features(state, perspective_player)
    return 25.0 * abs(count_delta) + 2.0 * abs(points_delta) + 8.0 * abs(mobility_delta) + 3.0 * abs(control_delta)


def _euclidean_distance(state: GameState, perspective_player: int) -> float:
    count_delta, points_delta, mobility_delta, control_delta = _relative_features(state, perspective_player)
    weighted = [25.0 * count_delta, 2.0 * points_delta, 8.0 * mobility_delta, 3.0 * control_delta]
    return sqrt(sum(value * value for value in weighted))
