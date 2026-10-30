# Operations workflow agent with approval gates and an audit trail

**Status: prototype (personal project).** A 40-request operations queue where an agent may act unattended only
when a written policy says the action is low-risk. Everything else needs one or two human approvals, and three
action types may never be run by the agent at all. Every attempt — executed or refused — lands in a hash-chained
audit log, so the record cannot be quietly rewritten afterwards.

The requests are **synthetic**. Nothing here comes from an employer, a client or a real order book.

## Business problem

Automating operations work is easy to demo and hard to trust. The failure that hurts is not an agent that stops
when it is unsure — it is an agent that does something irreversible correctly: refunds the wrong batch, re-prices
the catalogue, deletes the records, and leaves a log that says it was fine. The useful question is not "can the
agent do the task" but "what is the smallest set of actions it may take without me, and can I prove afterwards
what it did".

So the policy decides the tier, not the agent. The agent proposes; the policy grades the risk; a human approves
above a threshold; the executor refuses anything the policy has not classified; the log chains every entry to the
one before it.

## What the agent does, and what stays with a human

| The agent | The human |
|---|---|
| Classifies each request and computes its risk score | Writes the policy: base risk per action, money and reach limits, the never-execute list |
| Executes `auto`-tier actions and records the result | Decides what may be `auto` in the first place |
| Prepares everything for the approval step, including the exact payload hash being approved | Approves or rejects; a requester can never approve their own request |
| Refuses anything below the tier it computes, and logs the refusal | Re-runs or escalates a refusal; blocked actions are done by hand in the admin console |
| Appends one hash-chained entry per attempt | Reviews the chain; an edit anywhere in it breaks the hashes after it |

## Tools

- Python 3 standard library only — no LLM call, no framework, no database. The gate and the audit chain are the
  deliverable; the "proposal" step is a deterministic rule table, not a language model, and is not presented as one.
- `scripts/policy.py` risk policy · `scripts/agent.py` gate + HMAC approval tokens · `scripts/audit.py` hash chain
- `tests/test_gates.py` — 21 unit tests, one per invariant

## Flow

```
request (action, amount_myr, blast_radius, requested_by)
        ↓
policy.tier()  ──►  blocked ────────────────► never executed, escalated to a human
        │
        ├─► auto ─────────────────────────► execute → audit
        │
        ├─► single_approval ──► 1 token ──► verify → execute → audit
        │
        └─► dual_approval ────► 2 tokens ─► verify → execute → audit

token = HMAC(request_id | action | payload_sha | approver | expiry)
verify = signature · request id · payload hash · not expired · approver ≠ requester · distinct approvers
refusal → audit entry with the rule that stopped it
```

## Measured results

Run once with a frozen clock (`scripts/run_p5.py`, `results/p5_results.json`):

| Metric | Result |
|---|---|
| Requests in the queue | 40 synthetic, 12 action types, 4 simulated requesters |
| Routed `auto` (no human) | 6 / 40 = 15.0% |
| Routed `single_approval` | 25 / 40 = 62.5% |
| Routed `dual_approval` | 6 / 40 = 15.0% |
| Routed `blocked` (agent may never run) | 3 / 40 = 7.5% |
| Executed unattended | 6 |
| Executed after approval | 29 |
| Rejected by the approver | 1 |
| Left unanswered by the approver → **not executed** | 1 |
| Blocked by policy | 3 |
| Executions below their required approval count | **0** |
| Audit entries (one per attempt) | 43 — 35 executed, 8 refused |
| Hash chain verifies on reload | yes |
| Gate bypass attempts refused | **9 / 9** |

### The nine bypass attempts

Each one is a real call against the real executor, in `scripts/run_p5.py`:

| Attempt | Stopped by | Rule |
|---|---|---|
| Execute a single-approval action with no approval | gate | `missing_approval` |
| Present an approval signed with a different key | signature check | `bad_signature` |
| Approve your own request | approver identity | `self_approval` |
| Present an approval that has expired | expiry check | `expired` |
| Move a valid approval onto a different request | token binding | `wrong_request` |
| Change the payload after the approval was signed | payload hash | `payload_mismatch` |
| Re-execute a request that already ran | replay check | `replay` |
| Execute a never-execute action with two valid approvals | policy ceiling | `policy_ceiling` |
| Edit an amount in the audit log | hash chain | detected at entry 35 |

The last row is the one that matters for review: the chain verified before the edit and broke at the edited entry
afterwards, so a doctored log is detectable rather than plausible.

## What this measures and what it does not

- It **does** measure the gate: the invariants are tested (21 tests) and the queue is checked for executions below
  their required approval count — zero.
- The approvals are **simulated** by a scripted stand-in approver: approve up to RM5,000, reject above it, and one
  request deliberately left unanswered. The gate mechanics are real code; the human decisions are not, and nothing
  here is evidence about how real approvers behave under load.
- Side effects are **simulated** — the executor records what it would have done instead of calling a store API.
- There is **no language model** in this prototype. It is a policy gate and an audit chain around a rule table. That
  is deliberate: approval gates are worth nothing if the thing deciding the risk is the thing being gated.
- The 15% unattended rate is a property of *this* policy on *this* queue, not a recommendation. A real deployment
  would tune the base risk table against its own incident history, which I do not have.

## Reproduce

```bash
cd projects/ops-workflow-agent
python3 scripts/make_requests.py       # regenerate the 40-request queue (deterministic)
python3 scripts/run_p5.py              # route the queue, run the 9 probes, write results/
python3 -m unittest discover -s tests -p "test_*.py" -v   # 21 tests
```

Artefacts: `results/p5_results.json`, `results/routing.json`, `results/audit_log.jsonl`.
