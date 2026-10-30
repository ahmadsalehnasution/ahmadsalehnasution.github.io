"""Operations workflow agent: propose -> policy gate -> human approval -> execute -> audit.

Invariants this module is built to satisfy (tests/test_gates.py checks each one):

  I1  An action whose policy tier is not `auto` cannot execute without valid approval.
  I2  An approval token is bound to (request id, action, payload hash, approver,
      expiry). It cannot be moved to another request, forged, reused or resurrected
      after expiry.
  I3  A requester cannot approve their own request; dual approval needs two
      different approvers.
  I4  A `blocked` action never executes, even with two valid approvals: policy is a
      ceiling, an approval is not a key.
  I5  Every attempt appends exactly one hash-chained audit entry; executed actions
      are distinguishable from refused ones in the log.
"""
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

import audit
import policy

TOKEN_TTL_SECONDS = 900


def payload_hash(action, payload):
    material = json.dumps({"action": action, "payload": payload}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


@dataclass
class ApprovalToken:
    request_id: str
    action: str
    payload_sha: str
    approver: str
    expires_at: int
    signature: str = ""


def _sign(secret, request_id, action, phash, approver, expires_at):
    body = "|".join([request_id, action, phash, approver, str(expires_at)])
    return hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()


def issue_token(secret, request, approver, ttl=TOKEN_TTL_SECONDS, now=None):
    now = int(now if now is not None else time.time())
    phash = payload_hash(request["action"], request["payload"])
    expires = now + ttl
    return ApprovalToken(
        request_id=request["id"],
        action=request["action"],
        payload_sha=phash,
        approver=approver,
        expires_at=expires,
        signature=_sign(secret, request["id"], request["action"], phash, approver, expires),
    )


class GateError(Exception):
    def __init__(self, rule, detail):
        super().__init__(f"{rule}: {detail}")
        self.rule = rule
        self.detail = detail


class Executor:
    def __init__(self, secret, log=None, clock=None):
        self.secret = secret
        self.log = log if log is not None else audit.AuditLog()
        self.executed = set()
        self.attempts = 0
        self.refusals = []
        self.clock = clock or (lambda: int(time.time()))

    # -- gate ---------------------------------------------------------------
    def _check(self, request, tokens):
        action, payload = request["action"], request["payload"]
        wanted = policy.tier(action, payload)

        if action in policy.NEVER_EXECUTE:
            raise GateError("policy_ceiling", f"{action} is never executed by the agent")
        if request["id"] in self.executed:
            raise GateError("replay", f"{request['id']} already executed")
        if wanted == policy.AUTO:
            return wanted, []
        if not tokens:
            raise GateError("missing_approval", f"tier {wanted} requires approval, none presented")

        need = policy.required_approvers(action, payload)
        if len(tokens) != need:
            raise GateError("wrong_approval_count", f"tier {wanted} needs {need}, got {len(tokens)}")

        now = self.clock()
        approvers = []
        for tok in tokens:
            expected = _sign(self.secret, tok.request_id, tok.action, tok.payload_sha, tok.approver, tok.expires_at)
            if not hmac.compare_digest(expected, tok.signature):
                raise GateError("bad_signature", f"token from {tok.approver} is not signed by this system")
            if tok.request_id != request["id"]:
                raise GateError("wrong_request", f"token issued for {tok.request_id}, presented on {request['id']}")
            if tok.payload_sha != payload_hash(action, payload):
                raise GateError("payload_mismatch", f"token binds a different payload for {request['id']}")
            if tok.expires_at <= now:
                raise GateError("expired", f"token for {request['id']} expired at {tok.expires_at}")
            if tok.approver == request["requested_by"]:
                raise GateError("self_approval", f"{tok.approver} cannot approve their own request")
            approvers.append(tok.approver)
        if len(set(approvers)) != len(approvers):
            raise GateError("duplicate_approver", f"two approvals from the same person: {approvers}")
        return wanted, approvers

    # -- execute ------------------------------------------------------------
    def execute(self, request, tokens=(), outcome_fn=None):
        self.attempts += 1
        action, payload = request["action"], request["payload"]
        try:
            tier, approvers = self._check(request, list(tokens))
        except GateError as err:
            self.refusals.append({"request_id": request["id"], "rule": err.rule, "detail": err.detail})
            self.log.append(
                {
                    "ts": self.clock(),
                    "event": "refused",
                    "request_id": request["id"],
                    "action": action,
                    "tier": policy.tier(action, payload),
                    "rule": err.rule,
                    "detail": err.detail,
                }
            )
            raise

        result = (outcome_fn or default_outcome)(request)
        self.executed.add(request["id"])
        entry = self.log.append(
            {
                "ts": self.clock(),
                "event": "executed",
                "request_id": request["id"],
                "action": action,
                "tier": tier,
                "approvers": sorted(approvers),
                "approvals_required": policy.required_approvers(action, payload),
                "payload_sha": payload_hash(action, payload),
                "amount_myr": payload.get("amount_myr", 0),
                "blast_radius": payload.get("blast_radius", 0),
                "result": result,
            }
        )
        return entry


def default_outcome(request):
    """Stand-in for the real side effect. Records what would have happened."""
    return {"simulated": True, "effect": f"{request['action']} applied to {request['id']}"}
