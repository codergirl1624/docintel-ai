"""
main.py
-------
DocIntel AI – FastAPI application entry point.

Run:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import DocumentRequest, DocumentResponse, ErrorResponse
from auth import get_api_key
from extractor import extract_text
from analyzer import (
    generate_summary,
    extract_entities,
    analyze_sentiment,
    detect_document_type,
)
from scorer import calculate_dis, generate_insights

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("docintel")

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="DocIntel AI",
    description="Intelligent Document Analysis, Prioritization & Insight API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Root Route (optional but useful)
# ---------------------------------------------------------------------------
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "DocIntel AI is running successfully",
        "docs": "/docs",
        "health": "/health",
    }

# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "DocIntel AI"
    }

# ---------------------------------------------------------------------------
# Analyze Document Endpoint
# ---------------------------------------------------------------------------
@app.post(
    "/analyze",
    response_model=DocumentResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Unprocessable file"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["Analysis"],
    summary="Analyze a document and return structured intelligence report",
)
def analyze_document(
    request: DocumentRequest,
    api_key: str = Depends(get_api_key),
):
    logger.info("Received analysis request for: %s", request.fileName)

    # Step 1: Extract text
    text, extract_error = extract_text(
        request.fileType.value,
        request.fileBase64
    )

    if extract_error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Text extraction failed: {extract_error}",
        )

    logger.info(
        "Extracted %d characters from %s",
        len(text),
        request.fileName
    )

    # Step 2: Detect document type
    doc_type = detect_document_type(text)

    # Step 3: Generate summary
    summary = generate_summary(text)

    # Step 4: Extract entities
    entities = extract_entities(text)

    # Step 5: Sentiment
    sentiment = analyze_sentiment(text)

    # Step 6: Priority score
    priority_score, priority_level = calculate_dis(
        text,
        entities,
        sentiment,
        doc_type
    )

    # Step 7: Generate insights
    insights = generate_insights(
        text,
        entities,
        sentiment,
        doc_type,
        priority_score,
        priority_level
    )

    logger.info(
        "Analysis complete | File=%s | Score=%d | Level=%s | Sentiment=%s",
        request.fileName,
        priority_score,
        priority_level,
        sentiment,
    )

    return DocumentResponse(
        status="success",
        fileName=request.fileName,
        summary=summary,
        entities=entities,
        sentiment=sentiment,
        priority_score=priority_score,
        priority_level=priority_level,
        insights=insights,
    )

# ---------------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)

    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail
            },
        )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error."
        },
    )