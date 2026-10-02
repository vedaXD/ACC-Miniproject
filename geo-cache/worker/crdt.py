"""
CRDT engine.

- LWWRegister: for general key-value data. Highest HLC timestamp wins;
  node_id is the deterministic tie-breaker (handled inside hlc.compare).

- PNCounter: for numeric counters (e.g. likes). Each region tracks its own
  increment/decrement totals; merging just takes per-region maxima, so
  no increments are ever lost and merges are commutative + idempotent.
"""

from hlc import compare as hlc_compare


class LWWRegister:
    """value + hlc_timestamp, stored per key."""

    @staticmethod
    def merge(local_entry, remote_entry):
        """
        Each entry is {"value": ..., "ts": (physical, counter, node_id)}.
        Returns whichever entry wins (or local_entry if remote is None).
        """
        if local_entry is None:
            return remote_entry
        if remote_entry is None:
            return local_entry
        return remote_entry if hlc_compare(remote_entry["ts"], local_entry["ts"]) > 0 else local_entry


class PNCounter:
    """
    State shape per key: {"P": {node_id: count}, "N": {node_id: count}}
    Value = sum(P) - sum(N). Merge = per-node max (idempotent, commutative).
    """

    @staticmethod
    def new_state():
        return {"P": {}, "N": {}}

    @staticmethod
    def increment(state, node_id, amount=1):
        if amount >= 0:
            state["P"][node_id] = state["P"].get(node_id, 0) + amount
        else:
            state["N"][node_id] = state["N"].get(node_id, 0) + abs(amount)
        return state

    @staticmethod
    def value(state):
        return sum(state["P"].values()) - sum(state["N"].values())

    @staticmethod
    def merge(local_state, remote_state):
        if local_state is None:
            return remote_state
        if remote_state is None:
            return local_state
        merged = {"P": {}, "N": {}}
        for bucket in ("P", "N"):
            keys = set(local_state[bucket]) | set(remote_state[bucket])
            for k in keys:
                merged[bucket][k] = max(local_state[bucket].get(k, 0), remote_state[bucket].get(k, 0))
        return merged
