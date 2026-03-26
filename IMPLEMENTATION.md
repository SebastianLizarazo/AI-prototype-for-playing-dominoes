# AI Dominoes Prototype (Academic MVP)

## Scope

- 2 players
- Double-six set (28 tiles)
- Simplified round: each player gets 7 tiles, remaining tiles are not drawn
- Round ends when one player empties hand or both players pass consecutively
- Winner in blocked round: player with fewer points in hand

## AI Approach

- Decision algorithms:
	- **Minimax sin poda** (`MinimaxAgent`)
	- **Minimax con Alpha-Beta pruning** (`AlphaBetaAgent`)
- Heuristics comparables:
	- `linear`
	- `manhattan`
	- `euclidean`
- Baselines para oponente fijo:
	- `greedy`
	- `random`
	- `alpha` (legacy)

### Why not A* as core algorithm?

A* is excellent for shortest-path/search-to-goal problems with a clear admissible heuristic.
Dominoes in competitive play is adversarial and turn-based against an opponent that actively minimizes your gain.
For this reason, Minimax + Alpha-Beta is better aligned with the problem.

## Project Structure

- `src/game`: game domain, reglas, estado, motor e instrumentación por jugada
- `src/ai`: heurísticas + Minimax configurable (con y sin poda)
- `src/agents`: agentes random, greedy, minimax, alpha-beta
- `src/benchmarking`: agregación estadística (media, std, IC95)
- `scripts/play_cli.py`: demo runner (`ai-vs-ai` o `human-vs-ai`)
- `scripts/run_tournament.py`: benchmark reproducible y exportación CSV/JSON
- `tests/`: pruebas unitarias e integración

## Experimental Architecture

### 1) Ejecución de partidas

- `play_match(..., collect_metrics=True)` registra por jugada:
	- tiempo de decisión (`elapsed_ms`)
	- tiempo de CPU (`cpu_ms`)
	- nodos explorados
	- podas realizadas
- También registra por partida:
	- ganador
	- turnos
	- diferencia de puntos

### 2) Comparación entre agentes

- `run_tournament.py` construye una grilla de estrategias:
	- `alpha_beta::{linear,manhattan,euclidean}`
	- `minimax::{linear,manhattan,euclidean}`
- Cada estrategia se evalúa contra **el mismo oponente fijo**.

### 3) Reproducibilidad y control de sesgo

- Se genera una lista de semillas base: `seed + i`.
- **Todas las estrategias usan exactamente esa misma lista**.
- Opcionalmente se activa `--swap-seats` para ejecutar cada semilla en ambos asientos y reducir sesgo por orden inicial.
- Misma configuración global para todas las corridas (`depth`, `matches`, reglas del juego).

### 4) Almacenamiento y agregación

- Exporta:
	- `benchmark_matches.csv` (métricas por partida)
	- `benchmark_moves.csv` (métricas por jugada)
	- `benchmark_summary.csv` (agregados por estrategia)
	- `benchmark_report.json` (configuración + resumen)
- Métricas agregadas:
	- `win_rate`
	- turnos promedio y desviación estándar
	- nodos promedio y desviación estándar
	- podas promedio y desviación estándar
	- tiempo promedio por jugada
	- latencia máxima
	- diferencia de puntos promedio y desviación estándar
	- IC95 para turnos y diferencia de puntos

## Heuristic-to-Utility conversion

Las tres heurísticas de distancia se transforman a utilidad con:

\[
U(s) = -D(s)
\]

Esto garantiza consistencia para Minimax: **menor distancia ⇒ mayor utilidad**.

- `linear`: suma ponderada de deltas de features
- `manhattan`: norma L1 ponderada
- `euclidean`: norma L2 ponderada

Features relativas utilizadas:

- diferencia de número de fichas
- diferencia de puntos en mano
- diferencia de movilidad legal
- diferencia de control de extremos

## Run

```bash
python scripts/play_cli.py --mode ai-vs-ai --depth 4 --seed 42
python scripts/play_cli.py --mode human-vs-ai --ai alpha --depth 4 --seed 42
python scripts/run_tournament.py --matches 30 --depth 4 --opponent greedy --seed 42 --swap-seats --out results
pytest -q
```

## Checklist de validez experimental

- Misma lista de semillas para todas las estrategias.
- Oponente fijo durante toda la comparación.
- Misma configuración de juego y profundidad.
- Medición consistente de tiempo por jugada.
- Conteo explícito de nodos y podas.
- Minimax sin poda no reutiliza condiciones de poda.
- Exportación en formatos analizables (CSV/JSON).
- `human-vs-ai` se mantiene sin cambios funcionales.

## Suggested figures/tables for report

1. Architecture diagram (Domain / AI / Agents / CLI)
2. Minimax tree snippet with Alpha-Beta pruned branches
3. Comparative table: Random vs Greedy vs Alpha-Beta (win rate, avg turns)
4. Plot: search depth vs average decision time

## Limitations

- No draw-from-stock mechanic (deliberate simplification)
- Perfect-information simplification in search state
- Heuristic tuning is manual and lightweight
- IC95 aproximado con 1.96 (normal approximation)
