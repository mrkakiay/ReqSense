# ...new file...
import os
import json
from typing import Dict, Any

DEFAULT_PARAMS = {
    "temperature": 0.2,
    "max_tokens": 400,
    "style": "concise",
    "few_shot": True
}

PROMPT_TEMPLATE = """Task: Given the stakeholder experience, propose one concise requirement and a short "why" justification.
Return ONLY a JSON object with keys:
{{"requirement_text","why_statement","priority","tags","confidence"}}

Example:
Experience: "Users cannot find saved reports quickly..."
JSON:
{{"requirement_text":"Add a 'Saved Reports' quick access with search.","why_statement":"Users waste time...","priority":"high","tags":["reports","ux"],"confidence":0.85}}

Now analyze the experience below and return JSON only.

Experience:
\"\"\"{experience_text}\"\"\"

Generation style: {style}
"""

def build_prompt(experience_text: str, params: Dict[str,Any]) -> str:
    p = DEFAULT_PARAMS.copy()
    p.update(params or {})
    style = p.get("style", "concise")
    return PROMPT_TEMPLATE.format(experience_text=experience_text.strip()[:4000], style=style)

def call_llm(prompt: str, params: Dict[str,Any]) -> Dict[str,Any]:
    """
    Implement provider call here. Return parsed JSON dict on success.
    This stub returns a mock suggestion — replace with real provider SDK (OpenAI, Anthropic, local LLM).
    Ensure you store raw_response and model_version in DB.
    """
    # Example: parse result from real API and return dict
    # For now return a safe mock to allow local development
    raw = json.dumps({
        "requirement_text": "Mock requirement for: " + (prompt[:120].replace("\n"," ")),
        "why_statement": "Generated for demo.",
        "priority": "medium",
        "tags": ["auto"],
        "confidence": 0.5
    })
    parsed = json.loads(raw)
    return {"parsed": parsed, "raw": raw, "model_version": "mock-0.1"}