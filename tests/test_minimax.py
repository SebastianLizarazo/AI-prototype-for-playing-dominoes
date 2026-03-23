from agents.players import AlphaBetaAgent, RandomAgent
from game.engine import create_initial_state, play_match
from game.rules import legal_moves


def test_alpha_beta_returns_legal_move() -> None:
    state = create_initial_state(seed=1)
    agent = AlphaBetaAgent(depth=2)
    move = agent.choose_move(state, 0)
    assert move in legal_moves(state, 0)


def test_match_finishes_with_random_agents() -> None:
    result = play_match(RandomAgent(), RandomAgent(), seed=1, max_turns=200)
    assert result.turns > 0
    assert result.turns <= 200
