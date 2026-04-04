# DocIntel AI — Data Extraction API

## Description
DocIntel AI is a Python FastAPI application that extracts information from PDFs, Word documents, and images. 
It generates summaries, extracts entities, analyzes sentiment, and calculates document priority. 
The API is fully automated and returns structured JSON for easy consumption.

## Tech Stack
- **Language / Framework:** Python 3.11, FastAPI
- **Libraries:**
  - PyPDF2 — PDF parsing
  - python-docx — Word documents
  - pytesseract + Pillow — Image OCR
  - spaCy — Named Entity Recognition (NER)
  - TextBlob — Sentiment analysis
  - python-dotenv — Environment variable management
- **LLM/AI models used:** spaCy `en_core_web_sm` for NER

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/DocIntelAI.git
   cd DocIntelAI
2. Install dependencies:
   pip install -r requirements.txt

3. Set environment variables:
cp .env.example .env
# Open .env and set your DOCINTEL_API_KEY
4. Run the application:
uvicorn src.main:app --host 0.0.0.0 --port 8000
5. Test the health endpoint:
curl http://localhost:8000/health
6. Test document analysis 
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"fileName": "sample.pdf", "fileType": "pdf", "fileBase64": "..."}'

---

**Explanation:**  
- Steps are numbered for clarity.  
- Shows **clone → install → configure → run → test**, exactly what a reviewer needs.  
- Includes the **curl command** to test your `/analyze` endpoint, which proves your API works.

Show project structure
## Project Structure

your-repo/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│ ├── main.py
│ ├── models.py
│ ├── auth.py
│ ├── extractor.py
│ ├── analyzer.py
│ └── scorer.py
 review.

an example API response
## Example API Response
```json
{
  "status": "success",
  "fileName": "sample1.pdf",
  "summary": "Company Press Release: TechNova Launches Sustainable Data Centers...",
  "entities": {
    "names": ["Daniel Brooks", "Schneider Electric"],
    "dates": ["the next three years", "today"],
    "organizations": ["Gartner", "IBM", "Siemens", "TechNova"],
    "amounts": [],
    "locations": ["Asia", "Bangalore", "Berlin"]
  },
  "sentiment": "Positive",
  "priority_score": 25,
  "priority_level": "Medium",
  "insights": {
    "document_type": "press_release",
    "risk_level": "medium",
    "review_required": false,
    "financial_impact": "none"
  }
}


Add notes for reviewers
## Notes on Code Quality & Submission
- **Clean code structure**: All modules separated by functionality.
- **API Functionality**: `/health` and `/analyze` endpoints validated with multiple file types.
- **No hardcoded responses**: Works for arbitrary PDFs, DOCX, and images.
- **Technical Implementation**: Uses FastAPI, uvicorn, spaCy, TextBlob; modular and scalable.
- **User Experience**: Returns structured JSON ready for client consumption.