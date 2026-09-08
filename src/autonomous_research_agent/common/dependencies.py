from functools import lru_cache

from autonomous_research_agent.agents.graph import build_research_graph


@lru_cache
def get_research_graph():
    return build_research_graph()
