import re
import pdfplumber
import json
from openai import OpenAI

def extract_text_from_pdf(file_bytes):
    """Extracts raw text content safely from an uploaded PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise RuntimeWarning(f"Error reading PDF content: {str(e)}")
    return text.strip()

def extract_claims_with_llm(text, api_key):
    """Uses gpt-4o-mini to scan and pull structured, testable facts out of raw text."""
    if not text:
        return []
        
    client = OpenAI(api_key=api_key)
    
    prompt = (
        "You are an expert fact-checker. Extract distinct, objective factual claims from the following text. "
        "Focus explicitly on: statistics, percentages, specific dates, financial data, and technical claims. "
        "Ignore opinions, marketing fluff, or ambiguous statements. "
        "For each claim, write a short, self-contained factual statement suitable for a web search engine query.\n\n"
        f"Text to evaluate:\n{text}\n\n"
        "Return the response strictly as a JSON object matching this structure:\n"
        "{\n  \"claims\": [\"Claim statement 1\", \"Claim statement 2\"]\n}"
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("claims", [])
    except Exception as e:
        raise RuntimeError(f"LLM claims extraction failed: {str(e)}")
