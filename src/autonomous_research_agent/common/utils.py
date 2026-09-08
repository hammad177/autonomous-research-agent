import hashlib
import uuid


def new_thread_id() -> str:
    """Generates a unique id used to track a single graph run (thread)
    across requests — this is what checkpointing keys off of to pause
    and resume a specific run later."""
    return str(uuid.uuid4())


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
