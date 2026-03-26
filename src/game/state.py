from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from game.domino import Tile


Side = Literal["L", "R"] 

# Estado del juego de dominó, incluyendo el tablero, las manos de los jugadores, el turno actual, conteo de pases consecutivos, estado de la ronda y ganador si la ronda ha terminado.
@dataclass(frozen=True, slots=True)
class Move:
    tile: Tile | None
    side: Side | None = None

    @property
    def is_pass(self) -> bool:
        return self.tile is None

    @staticmethod
    def pass_move() -> "Move":
        return Move(tile=None, side=None)


@dataclass(frozen=True, slots=True)
class GameState:
    board: tuple[Tile, ...]
    hands: tuple[tuple[Tile, ...], tuple[Tile, ...]]
    current_player: int
    consecutive_passes: int = 0
    round_over: bool = False
    winner: int | None = None

    @property
    def left_end(self) -> int | None:
        return None if not self.board else self.board[0].left

    @property
    def right_end(self) -> int | None:
        return None if not self.board else self.board[-1].right


def hand_points(hand: tuple[Tile, ...]) -> int:
    return sum(tile.points for tile in hand)
