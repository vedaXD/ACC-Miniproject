import os
import json
import time
import threading

import redis
import requests
from flask import Flask, request, jsonify

from hlc import HLC
from crdt import LWWRegister, PNCounter

REGION_ID = os.environ["REGION_ID"]
REDIS_HOST = os.environ["REDIS_HOST"]
PEERS = [p for p in os.environ.get("PEERS", "").split(",") if p]
SYNC_INTERVAL_MS = int(os.environ.get("SYNC_INTERVAL_MS", "500"))
SIMULATED_LATENCY_MS = int(os.environ.get("SIMULATED_LATENCY_MS", "0"))

app = Flask(__name__)
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
clock = HLC(REGION_ID)

# write-behind buffer: list of pending deltas to push to peers
buffer_lock = threading.Lock()
pending_deltas = []  # each: {"type": "lww"|"counter", "key": ..., "entry"/"state": ...}


def _lww_key(key):
    return f"lww:{key}"


def _counter_key(key):
    return f"counter:{key}"


@app.route("/set", methods=["POST"])
def set_key():
    """SET key=val (LWW-Register)."""
    body = request.get_json()
    key, value = body["key"], body["value"]
    ts = clock.tick()
    entry = {"value": value, "ts": list(ts)}

    existing_raw = r.get(_lww_key(key))
    existing = json.loads(existing_raw) if existing_raw else None
    existing_entry = {"value": existing["value"], "ts": tuple(existing["ts"])} if existing else None
    winner = LWWRegister.merge(existing_entry, {"value": value, "ts": ts})

    r.set(_lww_key(key), json.dumps({"value": winner["value"], "ts": list(winner["ts"])}))

    with buffer_lock:
        pending_deltas.append({"type": "lww", "key": key, "entry": {"value": winner["value"], "ts": list(winner["ts"])}})

    return jsonify({"status": "ok", "region": REGION_ID, "key": key, "value": winner["value"], "ts": winner["ts"]})


@app.route("/get/<key>", methods=["GET"])
def get_key(key):
    raw = r.get(_lww_key(key))
    if not raw:
        return jsonify({"key": key, "value": None})
    entry = json.loads(raw)
    return jsonify({"key": key, "value": entry["value"], "ts": entry["ts"], "region": REGION_ID})


@app.route("/incr", methods=["POST"])
def incr_counter():
    """Increment/decrement a PN-Counter."""
    body = request.get_json()
    key, amount = body["key"], body.get("amount", 1)

    raw = r.get(_counter_key(key))
    state = json.loads(raw) if raw else PNCounter.new_state()
    state = PNCounter.increment(state, REGION_ID, amount)
    r.set(_counter_key(key), json.dumps(state))

    with buffer_lock:
        pending_deltas.append({"type": "counter", "key": key, "state": state})

    return jsonify({"status": "ok", "region": REGION_ID, "key": key, "value": PNCounter.value(state)})


@app.route("/counter/<key>", methods=["GET"])
def get_counter(key):
    raw = r.get(_counter_key(key))
    state = json.loads(raw) if raw else PNCounter.new_state()
    return jsonify({"key": key, "value": PNCounter.value(state), "region": REGION_ID})


@app.route("/sync", methods=["POST"])
def receive_sync():
    """Receive a batch of deltas from a peer region and merge them in."""
    deltas = request.get_json().get("deltas", [])
    for delta in deltas:
        if delta["type"] == "lww":
            key = delta["key"]
            remote_entry = {"value": delta["entry"]["value"], "ts": tuple(delta["entry"]["ts"])}
            clock.update(remote_entry["ts"])

            existing_raw = r.get(_lww_key(key))
            existing = json.loads(existing_raw) if existing_raw else None
            existing_entry = {"value": existing["value"], "ts": tuple(existing["ts"])} if existing else None

            winner = LWWRegister.merge(existing_entry, remote_entry)
            r.set(_lww_key(key), json.dumps({"value": winner["value"], "ts": list(winner["ts"])}))

        elif delta["type"] == "counter":
            key = delta["key"]
            remote_state = delta["state"]
            raw = r.get(_counter_key(key))
            local_state = json.loads(raw) if raw else None
            merged = PNCounter.merge(local_state, remote_state)
            r.set(_counter_key(key), json.dumps(merged))

    return jsonify({"status": "merged", "region": REGION_ID, "count": len(deltas)})


def replication_loop():
    """Every SYNC_INTERVAL_MS, flush the pending buffer to all peers."""
    while True:
        time.sleep(SYNC_INTERVAL_MS / 1000)
        with buffer_lock:
            if not pending_deltas:
                continue
            batch = pending_deltas[:]
            pending_deltas.clear()

        if SIMULATED_LATENCY_MS > 0:
            time.sleep(SIMULATED_LATENCY_MS / 1000)

        MAX_BUFFER_SIZE = 5000  # cap to avoid unbounded growth during a long partition

        for peer in PEERS:
            try:
                requests.post(f"http://{peer}/sync", json={"deltas": batch}, timeout=2)
            except requests.RequestException as e:
                # Peer unreachable (e.g. simulated partition) - retry on the
                # NEXT cycle, but cap how much we re-buffer so a prolonged
                # partition can't grow memory without bound.
                with buffer_lock:
                    pending_deltas.extend(batch)
                    if len(pending_deltas) > MAX_BUFFER_SIZE:
                        overflow = len(pending_deltas) - MAX_BUFFER_SIZE
                        del pending_deltas[:overflow]
                        print(f"[{REGION_ID}] buffer capped, dropped {overflow} oldest deltas")
                print(f"[{REGION_ID}] sync to {peer} failed: {e}")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"region": REGION_ID, "status": "up", "peers": PEERS})


if __name__ == "__main__":
    t = threading.Thread(target=replication_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
