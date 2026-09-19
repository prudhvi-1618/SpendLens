from dataclasses import dataclass
from typing import Literal


RuleKind = Literal[
    "completed_transaction",
    "upcoming_payment",
    "financial_document",
    "refund",
    "subscription",
    "general_financial",
    "currency_amount",
    "sender",
    "negative",
]


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: str
    weight: int
    kind: RuleKind


POSITIVE_RULES: tuple[Rule, ...] = (
    Rule("payment_successful", r"\b(payment|transaction)\s+(successful|completed|confirmed)\b", 4, "completed_transaction"),
    Rule("payment_received", r"\bpayment\s+received\b", 4, "completed_transaction"),
    Rule("purchase_confirmed", r"\b(purchase|order)(\s+has\s+been)?\s+(confirmed|confirmation)\b", 4, "completed_transaction"),
    Rule("card_charged", r"\b(card\s+)?(was\s+)?charged\b", 4, "completed_transaction"),
    Rule("amount_debited", r"\b(amount\s+)?debited\b", 4, "completed_transaction"),
    Rule("paid", r"\bpaid\b", 2, "completed_transaction"),
    Rule("payment_due", r"\b(payment|amount|bill)\s+due\b", 4, "upcoming_payment"),
    Rule("upcoming_payment", r"\bupcoming\s+payment\b", 4, "upcoming_payment"),
    Rule("payment_scheduled", r"\bpayment\s+scheduled\b", 4, "upcoming_payment"),
    Rule("renewal_reminder", r"\brenewal\s+(coming\s+up|reminder|due)\b", 4, "upcoming_payment"),
    Rule("will_be_charged", r"\bwill\s+be\s+charged\b", 4, "upcoming_payment"),
    Rule("next_billing_date", r"\bnext\s+billing\s+date\b", 4, "upcoming_payment"),
    Rule("refund_processed", r"\brefund(\s+of\s+[\w\s.,]+)?\s+(initiated|processed|completed|successful)\b", 4, "refund"),
    Rule("amount_refunded", r"\b(amount|money)\s+refunded\b", 4, "refund"),
    Rule("credited_back", r"\bcredited\s+back\b", 4, "refund"),
    Rule("invoice", r"\binvoice\b", 3, "financial_document"),
    Rule("receipt", r"\breceipt\b", 3, "financial_document"),
    Rule("uber_trip", r"\b(your\s+)?(uber|zomato|swiggy|ola)\s+(trip|ride|order)\b", 4, "completed_transaction"),
    Rule("statement", r"\b(statement|bank\s+statement)\b", 3, "financial_document"),
    Rule("billing_document", r"\bbilling\b", 2, "financial_document"),
    Rule("subscription", r"\bsubscription\b", 2, "subscription"),
    Rule("subscription_renewal", r"\b(subscription|membership)\s+renew(al|ed)\b", 3, "subscription"),
    Rule("recurring_payment", r"\brecurring\s+payment\b", 3, "subscription"),
    Rule("billing_cycle", r"\bbilling\s+cycle\b", 2, "subscription"),
    Rule("monthly_plan", r"\b(monthly|annual)\s+plan\b", 2, "subscription"),
    Rule("transaction", r"\btransaction\b", 1, "general_financial"),
    Rule("payment", r"\bpayment\b", 1, "general_financial"),
    Rule("purchase", r"\bpurchase(d)?\b", 1, "general_financial"),
    Rule("charge", r"\bcharge\b", 1, "general_financial"),
    Rule("bill", r"\bbill\b", 1, "general_financial"),
    Rule("upi", r"\bupi\b", 2, "general_financial"),
    Rule("bank_transaction", r"\bbank\s+transaction\b", 3, "general_financial"),
    Rule("currency_inr", r"(\u20b9|\binr\b|\brs\.?\b)\s*\d|(\d[\d,]*(\.\d{1,2})?\s*(\binr\b|\brs\.?\b))", 2, "currency_amount"),
    Rule("currency_usd", r"(\$|\busd\b)\s*\d|(\d[\d,]*(\.\d{1,2})?\s*(\busd\b))", 2, "currency_amount"),
    Rule("currency_eur", r"(\u20ac|\beur\b)\s*\d|(\d[\d,]*(\.\d{1,2})?\s*(\beur\b))", 2, "currency_amount"),
    Rule("currency_gbp", r"(\u00a3|\bgbp\b)\s*\d|(\d[\d,]*(\.\d{1,2})?\s*(\bgbp\b))", 2, "currency_amount"),
    Rule("amount_total", r"\b(amount|total|subtotal|tax)\b", 1, "currency_amount"),
)


SENDER_RULES: tuple[Rule, ...] = (
    Rule("sender_billing", r"(^|[<\s])billing@", 2, "sender"),
    Rule("sender_invoice", r"(^|[<\s])invoice@", 2, "sender"),
    Rule("sender_payments", r"(^|[<\s])payments@", 2, "sender"),
    Rule("sender_receipts", r"(^|[<\s])receipts@", 2, "sender"),
    Rule("sender_orders", r"(^|[<\s])orders@", 1, "sender"),
    Rule("sender_noreply", r"(^|[<\s])(no-?reply|support)@", 1, "sender"),
)


NEGATIVE_RULES: tuple[Rule, ...] = (
    Rule("newsletter", r"\bnewsletter\b", -2, "negative"),
    Rule("unsubscribe", r"\bunsubscribe\b", -1, "negative"),
    Rule("promotion", r"\b(promotion|promotional|offer|sale|discount|coupon)\b", -1, "negative"),
    Rule("blog", r"\b(blog|article|post)\b", -3, "negative"),
    Rule("webinar", r"\b(webinar|event|announcement)\b", -3, "negative"),
    Rule("community_digest", r"\b(community\s+update|digest)\b", -3, "negative"),
    Rule("social_notification", r"\bsocial\s+notification\b", -3, "negative"),
    Rule("educational_payment_context", r"\b(learn|guide|explained|how|what)\b.{0,40}\b(payment|transaction|purchase)s?\b", -4, "negative"),
)


FINANCIAL_THRESHOLD = 5
NON_FINANCIAL_THRESHOLD = 0
