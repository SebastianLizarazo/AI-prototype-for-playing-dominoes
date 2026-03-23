from __future__ import annotations

from game.rules import legal_moves
from game.state import GameState, hand_points


def evaluate_state(state: GameState, perspective_player: int) -> float:
    if state.round_over:
        if state.winner is None:
            return hand_points(state.hands[1 - perspective_player]) - hand_points(state.hands[perspective_player])
        return 10_000.0 if state.winner == perspective_player else -10_000.0

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
