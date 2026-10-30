"""Append-only, hash-chained audit log.

Each entry carries the hash of the entry before it plus its own content, so any
edit to a past entry breaks every hash after it. This is tamper *evidence*, not
tamper prevention: a log that cannot be quietly rewritten is what makes an
automated action reviewable after the fact.
"""
import hashlib
import json

GENESIS = "0" * 64


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class AuditLog:
    def __init__(self, path=None):
        self.path = path
        self.entries = []
        if path:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    self.entries = [json.loads(line) for line in fh if line.strip()]
            except FileNotFoundError:
                self.entries = []

    def append(self, event):
        prev = self.entries[-1]["hash"] if self.entries else GENESIS
        body = dict(event)
        body["seq"] = len(self.entries) + 1
        body["prev_hash"] = prev
        body["hash"] = hashlib.sha256((prev + _canon(body)).encode("utf-8")).hexdigest()
        self.entries.append(body)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(_canon(body) + "\n")
        return body


def verify(entries):
    """Return (ok, first_bad_seq). ok is True only if the whole chain verifies."""
    prev = GENESIS
    for entry in entries:
        if entry.get("prev_hash") != prev:
            return False, entry.get("seq")
        body = {k: v for k, v in entry.items() if k != "hash"}
        if hashlib.sha256((prev + _canon(body)).encode("utf-8")).hexdigest() != entry.get("hash"):
            return False, entry.get("seq")
        prev = entry["hash"]
    return True, None
