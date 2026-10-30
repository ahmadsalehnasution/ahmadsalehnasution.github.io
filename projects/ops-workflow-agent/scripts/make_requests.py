"""Generate the synthetic operations queue (deterministic, no randomness).

Every request here is invented for this demo. Nothing comes from an employer,
a client or a real order book: the point is to exercise the approval gate, not
to describe anyone's business.
"""
import json
import os

ROWS = [
    # action, amount_myr, blast_radius, requested_by, summary
    ("schedule_social_post", 0, 40, "op.a", "Schedule the Monday gold-saving carousel on IG and FB"),
    ("schedule_social_post", 0, 900, "op.a", "Schedule the same post to LinkedIn and TikTok"),
    ("publish_article", 0, 120, "op.b", "Publish the drafted article on zakat emas"),
    ("publish_article", 0, 250, "op.b", "Publish the drafted article on spread beli/jual"),
    ("reply_customer_email", 0, 1, "op.c", "Reply to a question about delivery time"),
    ("reply_customer_email", 0, 1, "op.c", "Reply to a refund-status question"),
    ("update_product_copy", 0, 300, "op.b", "Fix a typo in the 1-gram product copy"),
    ("update_product_copy", 0, 4200, "op.b", "Rewrite the product copy across the catalogue"),
    ("schedule_social_post", 0, 30, "op.a", "Schedule a story about gold price weekly recap"),
    ("publish_article", 0, 8000, "op.b", "Publish a pillar article and push it to the newsletter list"),
    ("update_price_page", 0, 200, "op.d", "Refresh the buy-back price table"),
    ("update_price_page", 0, 400, "op.d", "Update the price page footnote on spread"),
    ("issue_refund", 120, 1, "op.c", "Refund a duplicate 1-gram order"),
    ("issue_refund", 380, 1, "op.c", "Refund a cancelled 5-gram order"),
    ("issue_refund", 1750, 1, "op.c", "Refund a bulk order after courier damage"),
    ("issue_refund", 4200, 9000, "op.c", "Refund a batch of orders after a pricing error"),
    ("send_newsletter", 0, 12000, "op.a", "Send the monthly newsletter to the list"),
    ("send_newsletter", 0, 300, "op.a", "Send a correction notice to last month's recipients"),
    ("update_price_page", 2500, 500, "op.d", "Apply a supplier price increase to the public page"),
    ("issue_refund", 90, 1, "op.c", "Refund a shipping fee"),
    ("schedule_social_post", 0, 60, "op.a", "Schedule a customer testimonial post"),
    ("publish_article", 0, 210, "op.b", "Publish the piece on gold vs inflation"),
    ("reply_customer_email", 0, 1, "op.c", "Answer a question on zakat calculation"),
    ("update_product_copy", 0, 800, "op.b", "Update the FAQ block on the product page"),
    ("update_price_page", 0, 90, "op.d", "Correct a rounded figure on the price page"),
    ("send_newsletter", 0, 15000, "op.a", "Send a promo campaign to the whole list"),
    ("issue_refund", 640, 1, "op.c", "Partial refund for a delayed order"),
    ("schedule_social_post", 0, 900, "op.a", "Schedule the week's three posts"),
    ("update_product_copy", 0, 150, "op.b", "Add the new certificate number to the product copy"),
    ("update_price_page", 0, 7000, "op.d", "Sync prices across all product pages"),
    ("bulk_price_change", 0, 9000, "op.d", "Apply a 4% price change across the catalogue"),
    ("bulk_price_change", 0, 3500, "op.d", "Apply a 1.5% price change to two products"),
    ("bulk_price_change", 0, 12000, "op.d", "Re-price the whole catalogue after a supplier revision"),
    ("refund_batch", 4800, 120, "op.c", "Batch refund 12 orders from the same incident"),
    ("refund_batch", 9200, 40, "op.c", "Batch refund 6 high-value orders"),
    ("change_payout_account", 0, 1, "op.d", "Change the payout bank account on the store"),
    ("delete_records", 0, 340, "op.b", "Delete the old draft records from the database"),
    ("rotate_api_key", 0, 1, "op.a", "Rotate the courier API key"),
    ("issue_refund", 2100, 1, "op.c", "Refund a large order after a bank transfer reversal"),
    ("reply_customer_email", 0, 1, "op.c", "Reply to a complaint about the price page being stale"),
]

REQUIRERS = {"op.a": "op.a", "op.b": "op.b", "op.c": "op.c", "op.d": "op.d"}


def build():
    queue = []
    for i, (action, amount, blast, who, summary) in enumerate(ROWS, start=1):
        queue.append(
            {
                "id": f"RQ-{i:03d}",
                "requested_by": who,
                "action": action,
                "payload": {"amount_myr": amount, "blast_radius": blast, "summary": summary},
                "source": "synthetic",
            }
        )
    return queue


if __name__ == "__main__":
    queue = build()
    assert len(queue) == 40, len(queue)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "data", "requests.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for req in queue:
            fh.write(json.dumps(req, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"wrote {len(queue)} requests to {path}")
