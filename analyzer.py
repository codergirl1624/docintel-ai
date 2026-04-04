"""
analyzer.py
-----------
Handles:
  - AI-powered summarization (spaCy sentence ranking)
  - Named Entity Recognition (spaCy + regex)
  - Sentiment Analysis (TextBlob)
  - Document type detection
  - Priority scoring
"""

import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
    return _nlp


# -------------------------------------------------------------------
# TEXT CLEANING
# -------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean OCR text by removing excessive spaces/newlines.
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------------------------------------------
# SUMMARY
# -------------------------------------------------------------------

SUMMARY_SENTENCE_COUNT = 3

_IMPORTANCE_KEYWORDS = {
    "invoice", "contract", "urgent", "deadline", "payment",
    "legal", "penalty", "amount", "total", "due",
    "overdue", "critical", "fraud", "audit"
}


def _sentence_score(sentence: str) -> float:
    lower = sentence.lower()
    score = len(sentence.split())

    for kw in _IMPORTANCE_KEYWORDS:
        if kw in lower:
            score += 10

    return score


def generate_summary(text: str) -> str:
    text = clean_text(text)

    try:
        nlp = _get_nlp()
        doc = nlp(text[:5000])

        sentences = [
            sent.text.strip()
            for sent in doc.sents
            if len(sent.text.strip()) > 20
        ]

        if not sentences:
            return text[:300]

        scored = sorted(
            sentences,
            key=_sentence_score,
            reverse=True
        )

        top = scored[:SUMMARY_SENTENCE_COUNT]

        return " ".join(top)

    except Exception as exc:
        logger.warning("Summarization failed: %s", exc)
        return text[:300]


# -------------------------------------------------------------------
# ENTITY EXTRACTION
# -------------------------------------------------------------------

_AMOUNT_RE = re.compile(
    r"(?:₹|Rs\.?|INR|USD|\$|€|£)\s?[\d,]+(?:\.\d{1,2})?",
    re.IGNORECASE
)


def extract_entities(text: str) -> Dict[str, list]:
    text = clean_text(text)

    entities = {
        "names": set(),
        "dates": set(),
        "organizations": set(),
        "amounts": set(),
        "locations": set(),
    }

    try:
        nlp = _get_nlp()
        doc = nlp(text[:8000])

        for ent in doc.ents:
            value = ent.text.strip()

            if len(value) < 2:
                continue

            if ent.label_ == "PERSON":
                entities["names"].add(value)

            elif ent.label_ == "ORG":
                entities["organizations"].add(value)

            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].add(value)

            elif ent.label_ in ["DATE", "TIME"]:
                entities["dates"].add(value)

            elif ent.label_ == "MONEY":
                entities["amounts"].add(value)

        for match in _AMOUNT_RE.finditer(text):
            entities["amounts"].add(match.group().strip())

    except Exception as exc:
        logger.warning("NER failed: %s", exc)

    return {k: sorted(list(v)) for k, v in entities.items()}


# -------------------------------------------------------------------
# SENTIMENT
# -------------------------------------------------------------------

def analyze_sentiment(text: str) -> str:
    text = clean_text(text)

    try:
        from textblob import TextBlob

        blob = TextBlob(text[:3000])
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"

    except Exception as exc:
        logger.warning("Sentiment failed: %s", exc)
        return "Neutral"


# -------------------------------------------------------------------
# DOCUMENT TYPE
# -------------------------------------------------------------------

_DOC_TYPE_KEYWORDS = {
    "invoice": ["invoice", "bill", "tax invoice", "due date"],
    "contract": ["agreement", "contract", "clause"],
    "resume": ["skills", "education", "experience", "cv"],
    "complaint": ["complaint", "refund", "issue"],
    "report": ["report", "analysis", "findings"],
    "receipt": ["receipt", "transaction", "payment received"],
    "press_release": ["press release", "announced", "launch"],
    "legal": ["court", "judgment", "plaintiff"],
}


def detect_document_type(text: str) -> str:
    lower = clean_text(text).lower()

    scores = {}

    for doc_type, keywords in _DOC_TYPE_KEYWORDS.items():
        scores[doc_type] = sum(
            1 for kw in keywords if kw in lower
        )

    best = max(scores, key=scores.get)

    return best if scores[best] > 0 else "general"


# -------------------------------------------------------------------
# PRIORITY
# -------------------------------------------------------------------

def calculate_priority(text: str) -> Tuple[int, str]:
    lower = clean_text(text).lower()

    score = 10

    if "urgent" in lower:
        score += 30

    if "invoice" in lower or "payment" in lower:
        score += 25

    if "deadline" in lower or "due date" in lower:
        score += 20

    if "fraud" in lower or "legal" in lower:
        score += 30

    if "complaint" in lower:
        score += 20

    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return score, level