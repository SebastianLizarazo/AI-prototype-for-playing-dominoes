# AI Dominoes Prototype (Academic MVP)

## Scope

- 2 players
- Double-six set (28 tiles)
- Simplified round: each player gets 7 tiles, remaining tiles are not drawn
- Round ends when one player empties hand or both players pass consecutively
- Winner in blocked round: player with fewer points in hand

## AI Approach

- Main technique: **Minimax with Alpha-Beta pruning**
- Support techniques: heuristic evaluation function
- Baselines for comparison: random and greedy agents

### Why not A* as core algorithm?

A* is excellent for shortest-path/search-to-goal problems with a clear admissible heuristic.
Dominoes in competitive play is adversarial and turn-based against an opponent that actively minimizes your gain.
For this reason, Minimax + Alpha-Beta is better aligned with the problem.

## Project Structure

- `src/game`: game domain, rules, state, engine
- `src/ai`: heuristics and Minimax Alpha-Beta
- `src/agents`: random, greedy, and alpha-beta agents
- `scripts/play_cli.py`: demo runner (`ai-vs-ai` or `human-vs-ai`)
- `scripts/run_tournament.py`: short benchmark for results
- `tests/`: unit and integration tests

## Run

```bash
python scripts/play_cli.py --mode ai-vs-ai --depth 4 --seed 42
python scripts/play_cli.py --mode human-vs-ai --ai alpha --depth 4 --seed 42
python scripts/run_tournament.py --matches 50 --depth 4 --opponent greedy --seed 42
pytest -q
```

## Suggested figures/tables for report

1. Architecture diagram (Domain / AI / Agents / CLI)
2. Minimax tree snippet with Alpha-Beta pruned branches
3. Comparative table: Random vs Greedy vs Alpha-Beta (win rate, avg turns)
4. Plot: search depth vs average decision time

## Limitations

- No draw-from-stock mechanic (deliberate simplification)
- Perfect-information simplification in search state
- Heuristic tuning is manual and lightweight
