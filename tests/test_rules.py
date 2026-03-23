from game.domino import Tile
from game.rules import apply_move, legal_moves
from game.state import GameState, Move


def test_opening_has_all_tiles_as_legal_moves() -> None:
    state = GameState(
        board=tuple(),
        hands=((Tile(0, 0), Tile(1, 2), Tile(3, 4)), (Tile(2, 2), Tile(5, 6))),
        current_player=0,
    )
    moves = legal_moves(state, 0)
    assert len(moves) == 3
    assert all(move.side == "R" for move in moves)


def test_apply_regular_move_updates_board_and_turn() -> None:
    state = GameState(
        board=(Tile(1, 4),),
        hands=((Tile(4, 6), Tile(0, 0)), (Tile(2, 2),)),
        current_player=0,
    )

    new_state = apply_move(state, Move(tile=Tile(4, 6), side="R"))
    assert new_state.right_end == 6
    assert new_state.current_player == 1
    assert Tile(4, 6) not in new_state.hands[0]


def test_two_passes_close_round() -> None:
    state = GameState(
        board=(Tile(1, 1),),
        hands=((Tile(2, 3),), (Tile(4, 5),)),
        current_player=0,
    )
    s1 = apply_move(state, Move.pass_move())
    s2 = apply_move(s1, Move.pass_move())
    assert s2.round_over is True
