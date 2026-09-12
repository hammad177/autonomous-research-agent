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


def process_stream_chunk(chunk: dict) -> list[dict]:
    """Converts one raw astream(stream_mode='updates') chunk into a list of
    SSE-ready event dicts. A chunk normally has one key (the node that just
    finished), but interrupts surface under a special '__interrupt__' key
    instead of a node name — handled distinctly so the client can tell an
    interrupt apart from ordinary node progress."""
    events = []
    for key, value in chunk.items():
        if key == "__interrupt__":
            interrupts = value if isinstance(value, (list, tuple)) else [value]

            for interrupt_obj in interrupts:
                payload = getattr(interrupt_obj, "value", interrupt_obj)

                if not isinstance(payload, dict):
                    payload = {"value": payload}

                events.append(
                    {
                        "type": "interrupt",
                        "interrupt_type": payload.pop("type", None),
                        **payload,
                    }
                )
        else:
            trace = value.get("trace", []) if isinstance(value, dict) else []
            events.append({"type": "node_update", "node": key, "trace": trace})
    return events
