class ResearchAgentError(Exception):
    """Base exception for errors raised within this project's own logic."""


class GraphExecutionError(ResearchAgentError):
    """Raised when a graph run fails in a way that should surface as a
    clean API error rather than a raw stack trace."""
