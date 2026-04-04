"""
analyzer.py
-----------
Handles:
  - AI-powered summarization  (spaCy sentence ranking)
  - Named Entity Recognition  (spaCy)
  - Sentiment Analysis        (TextBlob)
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-load heavy models so import cost is paid once at first call
# ---------------------------------------------------------------------------
_nlp = None
_textblob_imported = False


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy  # noqa: PLC0415
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
    return _nlp


# ---------------------------------------------------------------------------
# Summarization
# ---------------------------------------------------------------------------

SUMMARY_SENTENCE_COUNT = 3

# Simple keyword importance boosters
_IMPORTANCE_KEYWORDS = {
    "invoice", "contract", "urgent", "deadline", "payment", "legal",
    "penalty", "breach", "claim", "amount", "total", "due", "overdue",
    "critical", "complaint", "dispute", "fraud", "audit",
}


def _sentence_score(sentence: str) -> float:
    """Heuristic importance score for a sentence."""
    lower = sentence.lower()
    score = len(sentence.split())  # length bonus
    for kw in _IMPORTANCE_KEYWORDS:
        if kw in lower:
            score += 10
    return score


def generate_summary(text: str) -> str:
    """
    Return a 2-3 sentence extractive summary of `text`.
    Falls back to the first SUMMARY_SENTENCE_COUNT sentences if NLP fails.
    """
    try:
        nlp = _get_nlp()
        doc = nlp(text[:5000])  # cap to keep it fast
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
        if not sentences:
            return text[:300]

        scored = sorted(sentences, key=_sentence_score, reverse=True)
        top = scored[:SUMMARY_SENTENCE_COUNT]
        # Re-order by original position for readability
        top_set = set(top)
        ordered = [s for s in sentences if s in top_set]
        return " ".join(ordered)
    except Exception as exc:
        logger.warning("Summarization failed: %s", exc)
        return text[:300]


# ---------------------------------------------------------------------------
# Named Entity Extraction
# ---------------------------------------------------------------------------

# Regex patterns for amounts (supplement spaCy MONEY detection)
_AMOUNT_RE = re.compile(
    r"(?:₹|Rs\.?|INR|USD|\$|€|£)\s?[\d,]+(?:\.\d{1,2})?|[\d,]+(?:\.\d{1,2})?\s?(?:rupees?|dollars?|euros?)",
    re.IGNORECASE,
)


def extract_entities(text: str) -> Dict[str, list]:
    """
    Extract names, dates, organizations, monetary amounts, and locations
    from the document text using spaCy NER + regex.
    """
    entities: Dict[str, set] = {
        "names": set(),
        "dates": set(),
        "organizations": set(),
        "amounts": set(),
        "locations": set(),
    }

    try:
        nlp = _get_nlp()
        doc = nlp(text[:8000])

        label_map = {
            "PERSON": "names",
            "ORG": "organizations",
            "GPE": "locations",
            "LOC": "locations",
            "DATE": "dates",
            "TIME": "dates",
            "MONEY": "amounts",
            "CARDINAL": None,  # ignore bare numbers
        }

        for ent in doc.ents:
            key = label_map.get(ent.label_)
            if key:
                entities[key].add(ent.text.strip())

        # Regex-based amount capture (catches INR/₹ that spaCy may miss)
        for match in _AMOUNT_RE.finditer(text):
            entities["amounts"].add(match.group().strip())

    except Exception as exc:
        logger.warning("NER failed: %s", exc)

    return {k: sorted(v) for k, v in entities.items()}


# ---------------------------------------------------------------------------
# Sentiment Analysis
# ---------------------------------------------------------------------------

def analyze_sentiment(text: str) -> str:
    """
    Return 'Positive', 'Neutral', or 'Negative' using TextBlob polarity.
    Polarity range: -1.0 (most negative) to +1.0 (most positive).
    """
    try:
        from textblob import TextBlob  # noqa: PLC0415
        blob = TextBlob(text[:3000])
        polarity = blob.sentiment.polarity
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"
    except Exception as exc:
        logger.warning("Sentiment analysis failed: %s", exc)
        return "Neutral"


# ---------------------------------------------------------------------------
# Document type detection (heuristic)
# ---------------------------------------------------------------------------

_DOC_TYPE_KEYWORDS: Dict[str, list] = {
    "invoice":   ["invoice", "bill", "total amount", "due date", "gst", "tax invoice"],
    "contract":  ["agreement", "contract", "parties", "clause", "obligations", "hereby"],
    "resume":    ["experience", "education", "skills", "objective", "curriculum vitae", "cv"],
    "complaint": ["complaint", "issue", "dissatisfied", "poor service", "refund", "escalate"],
    "report":    ["report", "analysis", "findings", "recommendation", "summary"],
    "receipt":   ["receipt", "payment received", "transaction", "order id"],
    "legal":     ["court", "judgment", "plaintiff", "defendant", "jurisdiction", "act", "section"],
}


def detect_document_type(text: str) -> str:
    lower = text.lower()
    scores: Dict[str, int] = {}
    for doc_type, keywords in _DOC_TYPE_KEYWORDS.items():
        scores[doc_type] = sum(1 for kw in keywords if kw in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"
