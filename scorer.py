"""
scorer.py
---------
Document Intelligence Score (DIS) engine.

Produces a 0-100 priority score and derived business insights.
"""

import re
from typing import Dict, Any, Tuple

# ---------------------------------------------------------------------------
# Keyword sets
# ---------------------------------------------------------------------------

_URGENT_KEYWORDS = {
    "urgent", "immediately", "asap", "critical", "overdue", "deadline",
    "penalty", "breach", "legal action", "final notice", "escalate",
    "court", "lawsuit", "arbitration", "injunction",
}

_LEGAL_KEYWORDS = {
    "contract", "agreement", "clause", "obligation", "liability",
    "jurisdiction", "indemnify", "plaintiff", "defendant", "judgment",
}

_FINANCIAL_KEYWORDS = {
    "invoice", "payment", "amount due", "total", "tax", "gst",
    "refund", "credit", "debit", "transaction", "billing",
}

# Regex to detect any monetary amount
_AMOUNT_RE = re.compile(
    r"(?:₹|Rs\.?|INR|USD|\$|€|£)\s?[\d,]+(?:\.\d{1,2})?",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _keyword_hit(text_lower: str, keywords: set) -> bool:
    return any(kw in text_lower for kw in keywords)


def calculate_dis(
    text: str,
    entities: Dict[str, list],
    sentiment: str,
    doc_type: str,
) -> Tuple[int, str]:
    """
    Calculate Document Intelligence Score (DIS).

    Returns:
        (score: int 0-100, priority_level: str)
    """
    score = 0
    text_lower = text.lower()

    # --- Monetary amounts detected ---
    if entities.get("amounts") or _AMOUNT_RE.search(text):
        score += 30

    # --- Negative sentiment (complaints, disputes) ---
    if sentiment == "Negative":
        score += 20

    # --- Legal / urgent keywords ---
    if _keyword_hit(text_lower, _URGENT_KEYWORDS):
        score += 20

    # --- Deadline / date references ---
    if entities.get("dates"):
        score += 15

    # --- Critical document types ---
    if doc_type in ("invoice", "contract", "legal", "complaint"):
        score += 15

    # --- Named organizations (indicates formal/business document) ---
    if entities.get("organizations"):
        score += 5

    # --- Positive sentiment slight boost (good news docs still matter) ---
    if sentiment == "Positive":
        score += 5

    # Clamp
    score = min(score, 100)

    # Derive priority level
    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    return score, level


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

def generate_insights(
    text: str,
    entities: Dict[str, list],
    sentiment: str,
    doc_type: str,
    priority_score: int,
    priority_level: str,
) -> Dict[str, Any]:
    """
    Generate business insight block for the response.
    """
    text_lower = text.lower()

    # Risk level
    if priority_level == "Critical":
        risk_level = "critical"
    elif priority_level == "High":
        risk_level = "high"
    elif priority_level == "Medium":
        risk_level = "medium"
    else:
        risk_level = "low"

    # Review required?
    review_required = (
        priority_level in ("Critical", "High")
        or sentiment == "Negative"
        or doc_type in ("contract", "legal", "complaint")
    )

    # Financial impact
    amounts = entities.get("amounts", [])
    if amounts:
        # Try to extract max numeric value to gauge impact
        nums = []
        for amt in amounts:
            digits = re.sub(r"[^\d.]", "", amt)
            try:
                nums.append(float(digits))
            except ValueError:
                pass
        max_val = max(nums) if nums else 0
        if max_val >= 100_000:
            financial_impact = "high"
        elif max_val >= 10_000:
            financial_impact = "medium"
        else:
            financial_impact = "low"
    elif _keyword_hit(text_lower, _FINANCIAL_KEYWORDS):
        financial_impact = "medium"
    else:
        financial_impact = "none"

    return {
        "document_type": doc_type,
        "risk_level": risk_level,
        "review_required": review_required,
        "financial_impact": financial_impact,
    }
