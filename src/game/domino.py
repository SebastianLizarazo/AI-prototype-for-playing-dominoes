from __future__ import annotations

from dataclasses import dataclass

# Ficha de dominó, con dos valores enteros entre 0 y 6 (inclusive).
@dataclass(frozen=True, slots=True)
class Tile:
    left: int
    right: int

    def flipped(self) -> "Tile": # Devuelve una nueva ficha con los valores intercambiados.
        return Tile(self.right, self.left)

    def matches(self, value: int) -> bool: # Devuelve True si alguno de los valores de la ficha coincide con el valor dado.
        return self.left == value or self.right == value

    @property
    def points(self) -> int: # Devuelve la cantidad de puntos de la ficha.
        return self.left + self.right

    def __str__(self) -> str:
        return f"[{self.left}|{self.right}]"


def generate_double_six_set() -> list[Tile]:# Genera el conjunto de fichas de dominó estándar (28 fichas, desde [0|0] hasta [6|6]).
    return [Tile(a, b) for a in range(7) for b in range(a, 7)]
