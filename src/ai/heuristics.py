from __future__ import annotations

from game.rules import legal_moves
from game.state import GameState, hand_points

# La función de evaluación heurística para el estado del juego, utilizada por el agente minimax para valorar posiciones no terminales.
def evaluate_state(state: GameState, perspective_player: int) -> float: 
    if state.round_over:# Si la ronda ha terminado, asigna una puntuación alta positiva si el jugador en perspectiva ganó, o una puntuación alta negativa si perdió. Si es un empate, devuelve 0.
        if state.winner is None:
            return hand_points(state.hands[1 - perspective_player]) - hand_points(state.hands[perspective_player])
        return 10_000.0 if state.winner == perspective_player else -10_000.0
    
    # Para estados no terminales, calcula una puntuación basada en varios factores:
    my_hand = state.hands[perspective_player]
    opp_hand = state.hands[1 - perspective_player]

    # Diferencia en la cantidad de fichas en mano (más fichas para el oponente es mejor para el jugador en perspectiva).
    my_count = len(my_hand)
    opp_count = len(opp_hand)
    score = (opp_count - my_count) * 25.0

    # Diferencia en puntos de las fichas en mano (menos puntos para el jugador en perspectiva es mejor).
    my_points = hand_points(my_hand)
    opp_points = hand_points(opp_hand)
    score += (opp_points - my_points) * 2.0

    # Movilidad (más movimientos legales disponibles para el jugador en perspectiva es mejor).
    my_mobility = len(legal_moves(state, perspective_player))
    opp_mobility = len(legal_moves(state, 1 - perspective_player))
    score += (my_mobility - opp_mobility) * 8.0

    # Control de los extremos (tener más fichas que coincidan con los extremos del tablero es mejor para el jugador en perspectiva).
    left_end = state.left_end
    right_end = state.right_end
    # Si ambos extremos están definidos, calcula cuántas fichas en la mano de cada jugador pueden jugar en esos extremos y ajusta la puntuación en consecuencia.
    if left_end is not None and right_end is not None:
        my_control = sum(1 for t in my_hand if t.left in (left_end, right_end) or t.right in (left_end, right_end))# Cuenta cuántas fichas en la mano del jugador en perspectiva pueden jugar en los extremos del tablero.
        opp_control = sum(1 for t in opp_hand if t.left in (left_end, right_end) or t.right in (left_end, right_end))# Cuenta cuántas fichas en la mano del oponente pueden jugar en los extremos del tablero.
        score += (my_control - opp_control) * 3.0# Ajusta la puntuación en función de la diferencia en el control de los extremos.

    my_unique_values = len({value for tile in my_hand for value in (tile.left, tile.right)})# Cuenta cuántos valores únicos (0-6) tiene el jugador en perspectiva en su mano. Tener más valores únicos puede ser ventajoso para mantener opciones de juego abiertas.
    score += my_unique_values * 1.5 # Ajusta la puntuación en función de la cantidad de valores únicos en la mano del jugador en perspectiva.

    return score
