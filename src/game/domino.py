from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Tile:
    left: int
    right: int

    def flipped(self) -> "Tile":
        return Tile(self.right, self.left)

    def matches(self, value: int) -> bool:
        return self.left == value or self.right == value

    @property
    def points(self) -> int:
        return self.left + self.right

    def __str__(self) -> str:
        return f"[{self.left}|{self.right}]"


def generate_double_six_set() -> list[Tile]:
    return [Tile(a, b) for a in range(7) for b in range(a, 7)]
