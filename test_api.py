"""
test_api.py
-----------
Quick smoke-test for the DocIntel AI API.
Encodes a sample text as a fake PDF (plain text base64) and hits /analyze.

Usage:
    python test_api.py
"""

import base64
import json
import requests

BASE_URL = "http://localhost:8000"
API_KEY  = "your_secret_api_key_here"   # must match DOCINTEL_API_KEY in .env

SAMPLE_TEXT = """
INVOICE
Issued by: ABC Pvt Ltd
To: Ravi Kumar
Date: 10 March 2026
Invoice No: INV-2026-0042

Description       Qty   Unit Price   Total
Consulting Services  5    ₹2,000     ₹10,000

Total Amount Due: ₹10,000
Payment Due Date: 25 March 2026

Please make payment immediately to avoid penalty.
Bank: HDFC Bank, Account: 0012345678, IFSC: HDFC0001234
"""

# Encode sample text as base64
encoded = base64.b64encode(SAMPLE_TEXT.encode("utf-8")).decode("utf-8")

payload = {
    "fileName": "test_invoice.pdf",
    "fileType": "pdf",
    "fileBase64": encoded,
}

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}


def test_analyze():
    resp = requests.post(f"{BASE_URL}/analyze", json=payload, headers=headers, timeout=30)
    print(f"Status Code : {resp.status_code}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


def test_invalid_key():
    bad_headers = {**headers, "x-api-key": "wrong_key"}
    resp = requests.post(f"{BASE_URL}/analyze", json=payload, headers=bad_headers, timeout=10)
    print(f"\n[Invalid key test] Status: {resp.status_code} → {resp.json()}")


def test_health():
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"\n[Health] {resp.json()}")


if __name__ == "__main__":
    test_health()
    test_analyze()
    test_invalid_key()
