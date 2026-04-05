# DocIntel AI — Intelligent Document Analysis & Extraction API

## Description
DocIntel AI is a Python FastAPI-based intelligent document analysis system that processes **PDF, DOCX, and image files**.

The system performs:
- **Text extraction**
- **Document summarization**
- **Named Entity Recognition (NER)**
- **Sentiment analysis**
- **Document priority scoring**
- **Insight generation**

The API returns structured JSON output for easy integration with web, mobile, or enterprise systems.

---

## Features
- Secure API key authentication
- PDF text extraction using PyPDF2
- DOCX extraction using python-docx
- OCR support for images using Tesseract OCR
- AI-powered entity extraction using spaCy
- Sentiment analysis using TextBlob
- Intelligent document type detection
- Priority scoring (Low / Medium / High)
- Business insights generation
- Swagger UI documentation
- Live public endpoint via ngrok

---

## Tech Stack
- **Language:** Python 3.11
- **Framework:** FastAPI
- **Server:** Uvicorn

### Libraries Used
- PyPDF2
- python-docx
- pytesseract
- Pillow
- spaCy
- TextBlob
- python-dotenv

### AI / NLP Models Used
- spaCy `en_core_web_sm`
- TextBlob sentiment engine

## Project Structure

```text
docintel/
├── main.py
├── auth.py
├── extractor.py
├── analyzer.py
├── scorer.py
├── models.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Clone repository
```bash
git clone https://github.com/codergirl1624/docintel-ai.git
cd docintel-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 4. Install TextBlob corpora
```bash
python -m textblob.download_corpora
```

### 5. Create environment file
```bash
cp .env.example .env
```

Add your API key inside `.env`:

```env
DOCINTEL_API_KEY=your_secret_api_key
```

### 6. Run the application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 7. Open Swagger documentation
After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check
```http
GET /health
```

### Document Analysis
```http
POST /analyze
```

### Required Header
```http
x-api-key: YOUR_API_KEY
```

### Example Request
```json
{
  "fileName": "sample.pdf",
  "fileType": "pdf",
  "fileBase64": "JVBERi0x..."
}
```

### Example Response
```json
{
  "status": "success",
  "fileName": "sample.pdf",
  "summary": "This is a payment invoice...",
  "entities": {
    "names": ["Ravi Kumar"],
    "dates": ["March 2026"],
    "organizations": ["ABC Pvt Ltd"],
    "amounts": ["₹10000"],
    "locations": []
  },
  "sentiment": "Neutral",
  "priority_score": 65,
  "priority_level": "High",
  "insights": {
    "document_type": "invoice",
    "risk_level": "high",
    "review_required": true,
    "financial_impact": "medium"
  }
}
```

## Architecture Overview

The project is modular and follows clean architecture principles.

main.py → API routes and request flow
auth.py → API key authentication
extractor.py → file text extraction
analyzer.py → NLP and intelligence layer
scorer.py → priority score + business insights
models.py → request / response schemas

## Security Implemented

API key authentication
Environment variable secret management
Constant-time key comparison using secrets.compare_digest()
CORS middleware support
Input validation using Pydantic schemas

## Live Deployment
Public API URL (submitted for evaluation):

https://nonvascularly-untelic-hadlee.ngrok-free.dev/analyze


## GitHub Repository
Repository Link:

https://github.com/codergirl1624/docintel-ai

---

## AI Tools Used
This project was developed with assistance from the following AI tools:

- ChatGPT (architecture guidance, debugging support, README documentation)
- GitHub Copilot / AI-assisted code suggestions (if used)
- spaCy NLP model (`en_core_web_sm`)
- TextBlob sentiment engine

All AI assistance has been disclosed as per hackathon submission guidelines.

---

## Challenges Faced
During development, the following technical challenges were addressed:

- API key authentication issue
- Environment variable loading issue
- Base64 decoding errors
- PDF text extraction edge cases
- OCR configuration using Tesseract
- Entity extraction improvement for organizations and locations
- Live public deployment under time constraints
- Maintaining stable endpoint availability using ngrok

---

## Known Limitations
- ngrok deployment is temporary and depends on local machine uptime
- OCR accuracy may vary for low-quality images
- Complex scanned PDFs may require advanced OCR tuning
- Current solution is API-first and does not include a dedicated frontend UI

---

## Submission Notes
This project was built for the **AI-Powered Document Analysis & Extraction** problem statement.

The submission includes:

- Live deployed endpoint
- Public GitHub repository
- API key authentication
- Full documentation
- Modular clean architecture
- AI-powered NLP workflow
- Production-ready API structure

This project was successfully validated using the official endpoint tester with status code 200.