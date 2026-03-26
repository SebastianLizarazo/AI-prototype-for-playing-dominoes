from __future__ import annotations

from dataclasses import dataclass
from math import inf

from ai.heuristics import evaluate_state
from game.rules import apply_move, legal_moves
from game.state import GameState, Move

#
@dataclass(slots=True)
class SearchStats:
    nodes: int = 0 # numero de nodos evaluados
    prunes: int = 0 # numero de ramas cortadas por poda alpha-beta


def choose_best_move(state: GameState, player: int, depth: int = 4) -> tuple[Move, SearchStats]:
    moves = legal_moves(state, player) # Obtener movimientos legales para el jugador actual
    if len(moves) == 1: # Si solo hay un movimiento legal, devolverlo sin necesidad de buscar
        return moves[0], SearchStats(nodes=1, prunes=0)

    # Inicializar variables para el algoritmo minimax con poda alpha-beta
    alpha = -inf 
    beta = inf
    best_value = -inf
    best_move = moves[0]
    stats = SearchStats()# Para contar nodos evaluados y ramas podadas

    # Ordenar los movimientos para mejorar la eficiencia de la poda alpha-beta, priorizando los movimientos que no son PASS.
    ordered_moves = sorted(moves, key=lambda m: 1 if m.is_pass else 0)
    for move in ordered_moves:
        child_state = apply_move(state, move)
        value = _minimax(
            state=child_state,
            depth=depth - 1,
            alpha=alpha,
            beta=beta,
            maximizing=False,
            perspective_player=player,
            stats=stats,
        )
        if value > best_value: # Si el valor de este movimiento es mejor que el mejor valor encontrado hasta ahora, actualizar el mejor valor y el mejor movimiento.
            best_value = value
            best_move = move
        alpha = max(alpha, best_value)

    return best_move, stats

# Función recursiva para el algoritmo minimax con poda alpha-beta. Evalúa el valor de un estado del juego desde la perspectiva de un jugador, considerando las posibles jugadas futuras hasta una cierta profundidad.
def _minimax(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    perspective_player: int,
    stats: SearchStats,
) -> float:
    stats.nodes += 1

    if depth == 0 or state.round_over:# Si se ha alcanzado la profundidad máxima o el juego ha terminado, evaluar el estado actual del juego desde la perspectiva del jugador.
        return evaluate_state(state, perspective_player)

    current_player = state.current_player
    moves = legal_moves(state, current_player) # Obtener movimientos legales para el jugador actual. Si no hay movimientos legales, se considerará un movimiento de PASS.
    ordered_moves = sorted(moves, key=lambda m: 1 if m.is_pass else 0)# Ordenar los movimientos para mejorar la eficiencia de la poda alpha-beta, priorizando los movimientos que no son PASS.

    # Si el jugador actual es el jugador en perspectiva, queremos maximizar el valor del estado del juego. 
    # Para cada movimiento legal, aplicamos el movimiento para obtener un nuevo estado del juego y llamamos recursivamente a _minimax para evaluar ese estado. 
    # Actualizamos alpha y realizamos poda beta si es posible.
    if maximizing:
        value = -inf
        for move in ordered_moves:
            child = apply_move(state, move)
            value = max(
                value,
                _minimax(
                    child,
                    depth - 1,
                    alpha,
                    beta,
                    maximizing=False,
                    perspective_player=perspective_player,
                    stats=stats,
                ),
            )
            alpha = max(alpha, value)
            if beta <= alpha:
                stats.prunes += 1
                break
        return value

    # Si el jugador actual no es el jugador en perspectiva, queremos minimizar el valor del estado del juego.
    value = inf
    for move in ordered_moves:
        child = apply_move(state, move)
        value = min(
            value,
            _minimax(
                child,
                depth - 1,
                alpha,
                beta,
                maximizing=True,
                perspective_player=perspective_player,
                stats=stats,
            ),
        )
        beta = min(beta, value)
        if beta <= alpha: # Si beta es menor o igual a alpha, se puede realizar poda alpha y no es necesario evaluar más movimientos en este nodo.
            stats.prunes += 1
            break
    return value
