import json


def format_sse(event: str, data: dict) -> str:
    """Formats a single SSE message. The blank line at the end is required
    by the SSE spec to terminate the event."""
    payload = json.dumps(data, default=str)
    return f"event: {event}\ndata: {payload}\n\n"
