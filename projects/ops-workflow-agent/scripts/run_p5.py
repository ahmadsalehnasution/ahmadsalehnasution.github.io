#!/usr/bin/env python3
"""Run the operations queue through the gate, then try to defeat the gate.

Two different things are measured:

  * the routing result -- how many of the 40 synthetic requests run without a
    human, how many wait for one or two, and how many the agent may never run;
  * the guarantee -- nine deliberate attempts to get an action executed without
    the approval policy requires, or to rewrite the record afterwards.

Approvals are simulated by a documented, deterministic stand-in approver (see
`scripted_approver`). The gate is real code; the humans are not.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import agent
import audit
import policy

SECRET = "demo-only-shared-secret"
CLOCK = 1_780_000_000  # frozen so the run is reproducible


def load_queue():
    with open(os.path.join(ROOT, "data", "requests.jsonl"), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def scripted_approver(request):
    """Stand-in for a human approver: deterministic and deliberately blunt.

    Approves up to RM5,000 and rejects above it. One request is left unanswered
    on purpose (RQ-039) to prove that silence is not approval.
    """
    if request["id"] == "RQ-039":
        return "silent"
    amount = float(request["payload"].get("amount_myr", 0) or 0)
    return "approve" if amount <= 5000 else "reject"


def run_queue():
    log = audit.AuditLog()
    ex = agent.Executor(SECRET, log=log, clock=lambda: CLOCK)
    routing = {"auto": 0, "single_approval": 0, "dual_approval": 0, "blocked": 0}
    outcomes = {"executed_auto": 0, "executed_after_approval": 0, "awaiting_approval": 0,
                "rejected_by_approver": 0, "blocked_by_policy": 0}
    rows = []
    for req in load_queue():
        t = policy.tier(req["action"], req["payload"])
        routing[t] += 1
        decision = scripted_approver(req)
        base = {"id": req["id"], "action": req["action"], "tier": t,
                "risk": policy.risk_score(req["action"], req["payload"])}
        if t == policy.BLOCKED:
            outcomes["blocked_by_policy"] += 1
            rows.append(dict(base, outcome="blocked_by_policy", approvers=[]))
            continue
        if t == policy.AUTO:
            ex.execute(req)
            outcomes["executed_auto"] += 1
            rows.append(dict(base, outcome="executed_auto", approvers=[]))
            continue
        if decision == "reject":
            outcomes["rejected_by_approver"] += 1
            rows.append(dict(base, outcome="rejected_by_approver", approvers=[]))
            continue
        if decision == "silent":
            outcomes["awaiting_approval"] += 1
            rows.append(dict(base, outcome="awaiting_approval", approvers=[]))
            continue
        approvers = ["lead.ops"] if t == policy.SINGLE else ["lead.ops", "lead.finance"]
        tokens = [agent.issue_token(SECRET, req, who, now=CLOCK) for who in approvers]
        ex.execute(req, tokens)
        outcomes["executed_after_approval"] += 1
        rows.append(dict(base, outcome="executed_after_approval", approvers=approvers))
    return ex, log, routing, outcomes, rows


def specimen(pid, action, amount, blast, who="op.c"):
    return {"id": pid, "requested_by": who, "action": action,
            "payload": {"amount_myr": amount, "blast_radius": blast,
                        "summary": "probe specimen"}, "source": "synthetic"}


def probes(ex, log, queue):
    """Nine deliberate attempts to defeat the gate. Each must be refused."""
    spec_single = specimen("PROBE-S1", "issue_refund", 500, 1)
    spec_other = specimen("PROBE-S2", "update_price_page", 0, 200, who="op.d")
    spec_blocked = specimen("PROBE-S3", "change_payout_account", 0, 1, who="op.d")
    executed = next(r for r in queue if r["id"] in ex.executed)
    checks = []

    def attempt(name, fn):
        try:
            fn()
        except agent.GateError as err:
            checks.append({"probe": name, "expected": "refused", "measured": "refused",
                           "rule": err.rule, "detail": err.detail})
        else:
            checks.append({"probe": name, "expected": "refused", "measured": "EXECUTED",
                           "rule": None, "detail": "gate failed to stop the attempt"})

    attempt("execute a single-approval action with no approval",
            lambda: ex.execute(spec_single, []))

    forged = agent.issue_token(SECRET, spec_single, "lead.ops", now=CLOCK)
    forged.signature = agent._sign("some-other-secret", forged.request_id, forged.action,
                                   forged.payload_sha, forged.approver, forged.expires_at)
    attempt("present an approval signed with a different key",
            lambda: ex.execute(spec_single, [forged]))

    attempt("approve your own request",
            lambda: ex.execute(spec_single, [agent.issue_token(SECRET, spec_single, "op.c", now=CLOCK)]))

    attempt("present an approval that has expired",
            lambda: ex.execute(spec_single, [agent.issue_token(SECRET, spec_single, "lead.ops", ttl=-10, now=CLOCK)]))

    attempt("move a valid approval onto a different request",
            lambda: ex.execute(spec_other, [agent.issue_token(SECRET, spec_single, "lead.ops", now=CLOCK)]))

    moved = json.loads(json.dumps(spec_single))
    tok = agent.issue_token(SECRET, moved, "lead.ops", now=CLOCK)
    moved["payload"]["amount_myr"] = 5000.0
    attempt("change the payload after the approval was signed",
            lambda: ex.execute(moved, [tok]))

    attempt("re-execute a request that already ran",
            lambda: ex.execute(executed, [agent.issue_token(SECRET, executed, "lead.ops", now=CLOCK),
                                          agent.issue_token(SECRET, executed, "lead.finance", now=CLOCK)]))

    attempt("execute a never-execute action with two valid approvals",
            lambda: ex.execute(spec_blocked, [agent.issue_token(SECRET, spec_blocked, "lead.ops", now=CLOCK),
                                              agent.issue_token(SECRET, spec_blocked, "lead.finance", now=CLOCK)]))

    ok_before, _ = audit.verify(log.entries)
    doctored = [dict(e) for e in log.entries]
    victim = next(e for e in reversed(doctored) if e["event"] == "executed")
    victim["amount_myr"] = 0.0
    ok_after, bad_seq = audit.verify(doctored)
    checks.append({"probe": "edit an amount in the audit log",
                   "expected": "detected",
                   "measured": "detected" if (ok_before and not ok_after) else "NOT DETECTED",
                   "rule": "audit_chain",
                   "detail": f"chain verified before the edit: {ok_before}; first broken entry after the edit: seq {bad_seq}"})
    return checks


def main():
    queue = load_queue()
    ex, log, routing, outcomes, rows = run_queue()
    checks = probes(ex, log, queue)

    exec_entries = [e for e in log.entries if e["event"] == "executed"]
    refused_entries = [e for e in log.entries if e["event"] == "refused"]
    unapproved = [e for e in exec_entries
                  if e["tier"] != policy.AUTO and len(e["approvers"]) < e["approvals_required"]]
    chain_ok, bad = audit.verify(log.entries)

    results = {
        "generated_at_utc": "2026-10-30",
        "clock_frozen_at": CLOCK,
        "requests": len(queue),
        "routing": routing,
        "outcomes": outcomes,
        "gate": {
            "attempts": ex.attempts,
            "refused_by_gate": len(ex.refusals),
            "refusal_rules": sorted({r["rule"] for r in ex.refusals}),
        },
        "audit": {
            "entries": len(log.entries),
            "executed_entries": len(exec_entries),
            "refused_entries": len(refused_entries),
            "chain_verified": chain_ok,
            "first_broken_seq": bad,
            "unapproved_executions": len(unapproved),
        },
        "probes": checks,
        "probes_refused": sum(1 for c in checks if c["measured"] in ("refused", "detected")),
        "probes_total": len(checks),
        "note": "Approvals are simulated by a scripted stand-in approver; the gate is real code. "
                "Side effects are simulated, not performed.",
    }

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    for name, payload in (("p5_results.json", results), ("routing.json", rows)):
        with open(os.path.join(ROOT, "results", name), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    with open(os.path.join(ROOT, "results", "audit_log.jsonl"), "w", encoding="utf-8") as fh:
        for e in log.entries:
            fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")

    print(json.dumps({k: results[k] for k in ("requests", "routing", "outcomes", "gate", "audit",
                                              "probes_refused", "probes_total")}, indent=2))
    for c in checks:
        print(f"  {c['measured']:>10}  {c['probe']}  -> {c['rule']}")


if __name__ == "__main__":
    main()
