"""Deterministic risk policy for the operations workflow agent.

The agent proposes an action; *policy* assigns its risk tier. The separation is
the point: an agent that grades its own risk can talk itself into anything, so
the tier is computed from the action type and the payload by fixed rules, and
the executor refuses to run below the tier it computes.
"""

AUTO = "auto"
SINGLE = "single_approval"
DUAL = "dual_approval"
BLOCKED = "blocked"

# Never executable by the agent, whatever approval is presented: irreversible
# destruction, or a change that belongs inside the admin console by a human.
NEVER_EXECUTE = {
    "change_payout_account",
    "delete_records",
    "rotate_api_key",
}

IRREVERSIBLE = {"delete_records", "bulk_price_change", "refund_batch"}

BASE_RISK = {
    "schedule_social_post": 4,
    "publish_article": 5,
    "reply_customer_email": 8,
    "update_product_copy": 14,
    "update_price_page": 22,
    "issue_refund": 28,
    "send_newsletter": 35,
    "bulk_price_change": 55,
    "refund_batch": 60,
    "rotate_api_key": 80,
    "change_payout_account": 90,
    "delete_records": 95,
}

# Money and reach are added to the base risk instead of replacing it, so a
# trivial action with a large blast radius is not treated as trivial.
LIMITS = {
    "auto_max_myr": 200.0,
    "auto_max_blast": 50,
    "single_max_myr": 2000.0,
    "single_max_blast": 5000,
}


def risk_score(action, payload):
    if action not in BASE_RISK:
        return 100.0
    score = float(BASE_RISK[action])
    amount = float(payload.get("amount_myr", 0) or 0)
    blast = int(payload.get("blast_radius", 0) or 0)
    score += min(25.0, amount / LIMITS["single_max_myr"] * 25.0)
    score += min(15.0, blast / LIMITS["single_max_blast"] * 15.0)
    return round(min(score, 100.0), 2)


def tier(action, payload):
    # Fail closed: an action the policy cannot classify is not auto-approved and
    # is not merely escalated -- it is refused, because nobody can approve a risk
    # the policy has never seen.
    if action in NEVER_EXECUTE or action not in BASE_RISK:
        return BLOCKED
    score = risk_score(action, payload)
    if score >= 60 or action in IRREVERSIBLE:
        return DUAL
    amount = float(payload.get("amount_myr", 0) or 0)
    blast = int(payload.get("blast_radius", 0) or 0)
    if score >= 20 or amount > LIMITS["auto_max_myr"] or blast > LIMITS["auto_max_blast"]:
        return SINGLE
    return AUTO


def required_approvers(action, payload):
    return {AUTO: 0, SINGLE: 1, DUAL: 2, BLOCKED: 0}[tier(action, payload)]
