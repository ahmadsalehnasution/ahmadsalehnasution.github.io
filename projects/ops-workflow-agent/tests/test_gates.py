"""Invariant tests for the approval gate and the audit chain.

These test the guarantee, not the demo output: an action that policy says needs a
human must not run without one, and an approval must not be reusable, forgeable,
movable or resurrectable. Run with:  python3 -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import agent
import audit
import policy
import run_p5

SECRET = "test-secret"
NOW = 1_780_000_000


def req(rid="T-001", action="issue_refund", amount=500, blast=1, who="op.c"):
    return {"id": rid, "requested_by": who, "action": action,
            "payload": {"amount_myr": amount, "blast_radius": blast, "summary": "test"},
            "source": "synthetic"}


def executor():
    return agent.Executor(SECRET, log=audit.AuditLog(), clock=lambda: NOW)


class PolicyTiers(unittest.TestCase):
    def test_low_risk_action_is_auto(self):
        self.assertEqual(policy.tier("schedule_social_post", {"blast_radius": 40}), policy.AUTO)

    def test_unknown_action_is_never_auto(self):
        self.assertEqual(policy.tier("rewrite_everything", {}), policy.BLOCKED)

    def test_never_execute_actions_are_blocked_whatever_the_payload(self):
        for action in ("delete_records", "change_payout_account", "rotate_api_key"):
            self.assertEqual(policy.tier(action, {"amount_myr": 0, "blast_radius": 1}), policy.BLOCKED)

    def test_large_refund_with_wide_reach_escalates_to_dual(self):
        self.assertEqual(policy.tier("issue_refund", {"amount_myr": 4200, "blast_radius": 9000}),
                         policy.DUAL)

    def test_irreversible_action_is_dual_even_when_small(self):
        self.assertEqual(policy.tier("bulk_price_change", {"amount_myr": 0, "blast_radius": 10}),
                         policy.DUAL)


class GateInvariants(unittest.TestCase):
    def test_auto_runs_without_approval(self):
        ex = executor()
        entry = ex.execute(req(action="schedule_social_post", amount=0, blast=40))
        self.assertEqual(entry["event"], "executed")
        self.assertEqual(entry["approvals_required"], 0)

    def test_single_refuses_without_approval(self):
        ex = executor()
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(req())
        self.assertEqual(ctx.exception.rule, "missing_approval")
        self.assertNotIn("T-001", ex.executed)

    def test_single_executes_with_one_approval(self):
        ex = executor()
        r = req()
        entry = ex.execute(r, [agent.issue_token(SECRET, r, "lead.ops", now=NOW)])
        self.assertEqual(entry["approvers"], ["lead.ops"])

    def test_dual_needs_two_and_refuses_one(self):
        ex = executor()
        r = req(action="bulk_price_change", amount=0, blast=900)
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, [agent.issue_token(SECRET, r, "lead.ops", now=NOW)])
        self.assertEqual(ctx.exception.rule, "wrong_approval_count")

    def test_dual_refuses_the_same_approver_twice(self):
        ex = executor()
        r = req(action="bulk_price_change", amount=0, blast=900)
        toks = [agent.issue_token(SECRET, r, "lead.ops", now=NOW),
                agent.issue_token(SECRET, r, "lead.ops", now=NOW)]
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, toks)
        self.assertEqual(ctx.exception.rule, "duplicate_approver")

    def test_self_approval_refused(self):
        ex = executor()
        r = req(who="op.c")
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, [agent.issue_token(SECRET, r, "op.c", now=NOW)])
        self.assertEqual(ctx.exception.rule, "self_approval")

    def test_expired_approval_refused(self):
        ex = executor()
        r = req()
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, [agent.issue_token(SECRET, r, "lead.ops", ttl=-1, now=NOW)])
        self.assertEqual(ctx.exception.rule, "expired")

    def test_forged_approval_refused(self):
        ex = executor()
        r = req()
        tok = agent.issue_token(SECRET, r, "lead.ops", now=NOW)
        tok.signature = agent._sign("attacker-secret", tok.request_id, tok.action,
                                    tok.payload_sha, tok.approver, tok.expires_at)
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, [tok])
        self.assertEqual(ctx.exception.rule, "bad_signature")

    def test_approval_cannot_move_to_another_request(self):
        ex = executor()
        a, b = req("T-A"), req("T-B")
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(b, [agent.issue_token(SECRET, a, "lead.ops", now=NOW)])
        self.assertEqual(ctx.exception.rule, "wrong_request")

    def test_payload_change_after_approval_refused(self):
        ex = executor()
        r = req(amount=500)
        tok = agent.issue_token(SECRET, r, "lead.ops", now=NOW)
        r["payload"]["amount_myr"] = 5000
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, [tok])
        self.assertEqual(ctx.exception.rule, "payload_mismatch")

    def test_replay_refused(self):
        ex = executor()
        r = req()
        ex.execute(r, [agent.issue_token(SECRET, r, "lead.ops", now=NOW)])
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, [agent.issue_token(SECRET, r, "lead.ops", now=NOW)])
        self.assertEqual(ctx.exception.rule, "replay")

    def test_blocked_action_refused_even_with_two_valid_approvals(self):
        ex = executor()
        r = req(action="change_payout_account", amount=0, blast=1)
        toks = [agent.issue_token(SECRET, r, "lead.ops", now=NOW),
                agent.issue_token(SECRET, r, "lead.finance", now=NOW)]
        with self.assertRaises(agent.GateError) as ctx:
            ex.execute(r, toks)
        self.assertEqual(ctx.exception.rule, "policy_ceiling")


class AuditInvariants(unittest.TestCase):
    def test_every_attempt_is_logged_once(self):
        ex = executor()
        r_ok = req("T-OK")
        ex.execute(r_ok, [agent.issue_token(SECRET, r_ok, "lead.ops", now=NOW)])
        try:
            ex.execute(req("T-NO"))
        except agent.GateError:
            pass
        self.assertEqual(len(ex.log.entries), 2)
        self.assertEqual([e["event"] for e in ex.log.entries], ["executed", "refused"])

    def test_chain_verifies_and_detects_an_edit(self):
        log = audit.AuditLog()
        for i in range(3):
            log.append({"event": "executed", "request_id": f"T-{i}", "tier": "auto"})
        ok, bad = audit.verify(log.entries)
        self.assertTrue(ok)
        self.assertIsNone(bad)
        doctored = [dict(e) for e in log.entries]
        doctored[1]["request_id"] = "T-EDITED"
        ok2, bad2 = audit.verify(doctored)
        self.assertFalse(ok2)
        self.assertEqual(bad2, 2)

    def test_written_log_reloads_and_still_verifies(self):
        path = os.path.join(ROOT, "results", ".test_audit.jsonl")
        if os.path.exists(path):
            os.remove(path)
        try:
            log = audit.AuditLog(path)
            log.append({"event": "executed", "request_id": "T-1"})
            log.append({"event": "refused", "request_id": "T-2"})
            reloaded = audit.AuditLog(path)
            self.assertEqual(len(reloaded.entries), 2)
            self.assertTrue(audit.verify(reloaded.entries)[0])
        finally:
            if os.path.exists(path):
                os.remove(path)


class FullQueue(unittest.TestCase):
    """The claim on the case-study page, checked rather than asserted."""

    def test_no_execution_below_its_required_approvals(self):
        ex, log, routing, outcomes, rows = run_p5.run_queue()
        self.assertEqual(len(rows), 40)
        self.assertEqual(sum(outcomes.values()), 40)
        executed = [e for e in log.entries if e["event"] == "executed"]
        breaches = [e for e in executed
                    if e["tier"] != policy.AUTO and len(e["approvers"]) < e["approvals_required"]]
        self.assertEqual(breaches, [])
        auto_ran = [e for e in executed if e["tier"] == policy.AUTO]
        self.assertTrue(all(e["approvers"] == [] for e in auto_ran))
        self.assertTrue(all(e["hash"] for e in log.entries))
        self.assertTrue(audit.verify(log.entries)[0])


if __name__ == "__main__":
    unittest.main()
