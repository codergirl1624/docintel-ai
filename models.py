from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class FileType(str, Enum):
    pdf = "pdf"
    docx = "docx"
    png = "png"
    jpg = "jpg"
    jpeg = "jpeg"


class DocumentRequest(BaseModel):
    fileName: str = Field(..., example="sample.pdf")
    fileType: FileType = Field(..., example="pdf")
    fileBase64: str = Field(..., description="Base64 encoded file content")


class Entities(BaseModel):
    names: List[str] = []
    dates: List[str] = []
    organizations: List[str] = []
    amounts: List[str] = []
    locations: List[str] = []


class Insights(BaseModel):
    document_type: str
    risk_level: str
    review_required: bool
    financial_impact: str


class DocumentResponse(BaseModel):
    status: str
    fileName: str
    summary: str
    entities: Entities
    sentiment: str
    priority_score: int
    priority_level: str
    insights: Insights


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
