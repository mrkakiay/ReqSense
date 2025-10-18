# ...new file...
import os
from src.app import create_app
from src.models import db, RequirementSuggestion, Experience
from src.services.llm import build_prompt, call_llm
from datetime import datetime, timezone

# create app context for worker
app = create_app()
app.app_context().push()

def generate_requirement_job(experience_id: int, params: dict = None):
    exp = Experience.query.get(experience_id)
    if not exp:
        return {"error": "experience not found", "experience_id": experience_id}
    # create suggestion record (processing)
    sug = RequirementSuggestion(
        experience_id=exp.id,
        status='processing',
        params=params or {}
    )
    db.session.add(sug)
    db.session.commit()

    try:
        prompt = build_prompt(exp.narrative_text or "", params or {})
        result = call_llm(prompt, params or {})
        parsed = result.get("parsed") or {}
        sug.requirement_text = parsed.get("requirement_text")
        sug.why_statement = parsed.get("why_statement")
        sug.priority = parsed.get("priority")
        sug.tags = parsed.get("tags")
        sug.confidence = float(parsed.get("confidence", 0.0) or 0.0)
        sug.raw_response = result.get("raw")
        sug.model_version = result.get("model_version")
        sug.status = 'done'
        sug.processed_at = datetime.now(timezone.utc)
        db.session.commit()
        return {"ok": True, "suggestion_id": sug.id}
    except Exception as e:
        sug.status = 'failed'
        sug.raw_response = (sug.raw_response or "") + f"\n\nERROR:{e}"
        db.session.commit()
        return {"ok": False, "error": str(e)}