"""A simple calculator tool for numeric sub-questions."""

from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Evaluates a basic arithmetic expression, e.g. '42 * 3.5' or '(120-15)/2'.
    Only use this for numeric calculations, not general questions."""
    try:
        allowed = "0123456789+-*/(). "
        if not all(ch in allowed for ch in expression):
            return "Error: expression contains disallowed characters."
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error evaluating expression: {e}"
