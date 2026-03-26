from __future__ import annotations

from game.domino import Tile
from game.state import GameState, Move, hand_points

# Reglas del juego de dominó, incluyendo generación de movimientos legales, aplicación de movimientos al estado del juego y cálculo de utilidad para estados terminales.
def legal_moves(state: GameState, player: int) -> list[Move]:
    if state.round_over:
        return []

    hand = state.hands[player]
    if not state.board:
        return [Move(tile=t, side="R") for t in hand]

    left_end = state.left_end
    right_end = state.right_end
    moves: list[Move] = []

    for tile in hand:
        if left_end is not None and tile.matches(left_end):
            moves.append(Move(tile=tile, side="L"))
        if right_end is not None and tile.matches(right_end):
            moves.append(Move(tile=tile, side="R"))

    if not moves:
        return [Move.pass_move()]

    return moves

# Aplica un movimiento al estado del juego, devolviendo el nuevo estado resultante después de la jugada.
# Valida que el movimiento sea legal antes de aplicarlo, actualiza el tablero, las manos de los jugadores, el turno actual y verifica si la ronda ha terminado.
def apply_move(state: GameState, move: Move) -> GameState:
    player = state.current_player
    hand = list(state.hands[player])
    board = list(state.board)
    next_player = 1 - player

    if move.is_pass:
        next_passes = state.consecutive_passes + 1
        round_over = next_passes >= 2
        winner = _winner_if_blocked(state) if round_over else None
        return GameState(
            board=tuple(board),
            hands=state.hands,
            current_player=next_player,
            consecutive_passes=next_passes,
            round_over=round_over,
            winner=winner,
        )

    if move.tile not in hand:
        raise ValueError("Tile not in current player's hand")

    hand.remove(move.tile)
    placed_tile = _orient_for_side(move.tile, move.side, state.left_end, state.right_end)
    if not board:
        board.append(placed_tile)
    elif move.side == "L":
        board.insert(0, placed_tile)
    elif move.side == "R":
        board.append(placed_tile)
    else:
        raise ValueError("Invalid side for non-pass move")

    new_hands = list(state.hands)
    new_hands[player] = tuple(hand)
    new_hands_tuple = (new_hands[0], new_hands[1])

    round_over = len(new_hands_tuple[player]) == 0
    winner = player if round_over else None

    return GameState(
        board=tuple(board),
        hands=new_hands_tuple,
        current_player=next_player,
        consecutive_passes=0,
        round_over=round_over,
        winner=winner,
    )


# Calcula la utilidad para un jugador dado en un estado terminal, devolviendo un valor positivo si el jugador gana, negativo si pierde o la diferencia de puntos si es un empate.
def utility_for_player(state: GameState, player: int) -> int:
    if not state.round_over:
        raise ValueError("Utility only defined for terminal states")

    if state.winner is None:
        my_points = hand_points(state.hands[player])
        opp_points = hand_points(state.hands[1 - player])
        return opp_points - my_points

    return 10_000 if state.winner == player else -10_000

# Orienta una ficha para que coincida con el extremo del tablero al que se va a colocar, devolviendo la ficha en la orientación correcta o lanzando un error si no es posible colocarla en ese lado.
def _orient_for_side(tile: Tile, side: str | None, left_end: int | None, right_end: int | None) -> Tile:
    if side is None:
        raise ValueError("Side is required for tile move")

    if left_end is None and right_end is None:
        return tile

    if side == "L":
        if tile.right == left_end:
            return tile
        if tile.left == left_end:
            return tile.flipped()
    elif side == "R":
        if tile.left == right_end:
            return tile
        if tile.right == right_end:
            return tile.flipped()

    raise ValueError("Tile does not match selected board side")

# Determina el ganador en caso de que ambos jugadores hayan pasado consecutivamente, devolviendo el jugador con menos puntos o None si es un empate.
def _winner_if_blocked(state: GameState) -> int | None:
    p0 = hand_points(state.hands[0])
    p1 = hand_points(state.hands[1])
    if p0 == p1:
        return None
    return 0 if p0 < p1 else 1
