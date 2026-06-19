import time
from duckduckgo_search import DDGS
from openai import OpenAI
import json

def search_live_web(query, max_results=3):
    """Fetches text snippets dynamically from the web matching a target query."""
    evidence_snippets = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            for res in results:
                evidence_snippets.append(f"Source: {res.get('href')}\nContent: {res.get('body')}")
    except Exception as e:
        # Gracefully log or handle transient network issues/rate limits
        evidence_snippets.append(f"Web search execution omitted or timed out. Error: {str(e)}")
    return "\n\n".join(evidence_snippets)

def cross_reference_claim(claim, web_evidence, api_key):
    """Evaluates a single claim against web evidence using an LLM evaluator."""
    client = OpenAI(api_key=api_key)
    
    prompt = (
        "Context Role: Senior Fact-Checking Analyst.\n"
        f"Target Claim to Verify: \"{claim}\"\n\n"
        f"Live Web Search Context Retrieved:\n{web_evidence}\n\n"
        "Instructions:\n"
        "Compare the target claim thoroughly against the provided context. Formulate your judgment.\n"
        "Classify the status precisely into one of these buckets:\n"
        "- VERIFIED: The claim is fully accurate and supported by evidence.\n"
        "- INACCURATE: The claim contains slight modifications, misstated dates, numbers, or distortions, but is based on real events.\n"
        "- FALSE: The claim contradicts reality completely or has zero factual backing.\n\n"
        "Return your analysis strictly as a JSON object matching this schema:\n"
        "{\n"
        "  \"status\": \"VERIFIED | INACCURATE | FALSE\",\n"
        "  \"correct_information\": \"Provide accurate data if mismatched, or state validation summary.\",\n"
        "  \"confidence_score\": 85\n"
        "}\n"
        "Note: confidence_score must be an integer between 0 and 100."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "status": "INACCURATE",
            "correct_information": "Verification process encountered an evaluation exception.",
            "confidence_score": 0
        }
