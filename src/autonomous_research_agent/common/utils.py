import hashlib
import uuid


def new_thread_id() -> str:
    """Generates a unique id used to track a single graph run (thread)
    across requests — this is what checkpointing keys off of to pause
    and resume a specific run later."""
    return str(uuid.uuid4())


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_pending_interrupt(result: dict) -> dict | None:
    """If a graph invocation paused on an interrupt, pulls out the
    payload the node passed to interrupt() so the API can show it."""
    interrupts = result.get("__interrupt__")
    if not interrupts:
        return None
    first = interrupts[0]
    return getattr(first, "value", first)
