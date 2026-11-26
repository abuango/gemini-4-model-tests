from .money import allocate


def cost_per_team(cost, headcount):
    """headcount maps team to people. Returns each team's share of cost."""
    teams = list(headcount)
    return dict(zip(teams, allocate(cost, [headcount[t] for t in teams])))
