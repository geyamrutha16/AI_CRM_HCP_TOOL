"""
LangChain tools for the CRM agent.
Each tool handles specific CRM operations with LLM-powered intelligence.
"""

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from models.database import Interaction
from datetime import datetime
import json
import re
from time import perf_counter
import config


# Initialize Groq LLM
llm = ChatGroq(
    temperature=0.7,
    model_name=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY
)


class LogInteractionInput(BaseModel):
    """Input schema for LogInteractionTool."""
    doctor_name: str = Field(..., description="Name of the healthcare professional")
    interaction_text: str = Field(..., description="Raw interaction conversation text")


class EditInteractionInput(BaseModel):
    """Input schema for EditInteractionTool."""
    interaction_id: int = Field(..., description="ID of interaction to edit")
    field: str = Field(..., description="Field to update: summary, sentiment, follow_up")
    new_value: str = Field(..., description="New value for the field")


class FetchInteractionInput(BaseModel):
    """Input schema for FetchInteractionTool."""
    doctor_name: Optional[str] = Field(None, description="Filter by doctor name")
    limit: int = Field(10, description="Number of interactions to fetch")


class SuggestNextActionInput(BaseModel):
    """Input schema for SuggestNextActionTool."""
    interaction_id: int = Field(..., description="ID of the interaction")
    context: Optional[str] = Field(None, description="Additional context")


class SummarizeInteractionInput(BaseModel):
    """Input schema for SummarizeInteractionTool."""
    interaction_text: str = Field(..., description="Long interaction text to summarize")


def log_interaction_tool(doctor_name: str, interaction_text: str, db_session: Session = None) -> dict:
    """
    Logs a new HCP interaction using AI extraction.
    
    - Extracts doctor_name, summary, sentiment, and follow_up using LLM
    - Saves to database
    - Returns structured interaction data
    """
    
    started_at = perf_counter()
    print("[DEBUG][TOOL] log_interaction_tool start")

    text = interaction_text.strip()
    extracted_doctor = doctor_name
    if not extracted_doctor:
        match = re.search(r"\b(?:dr\.?|doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", interaction_text)
        extracted_doctor = f"Dr. {match.group(1)}" if match else "Unknown"

    lower_text = interaction_text.lower()
    if "positive" in lower_text:
        sentiment = "positive"
    elif "negative" in lower_text:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    follow_up_match = re.search(
        r"(?:follow[\s-]?up(?: action)?(?: as| is|:)?\s*)([^,.]+)",
        interaction_text,
        re.IGNORECASE,
    )
    follow_up = follow_up_match.group(1).strip() if follow_up_match else "Follow up in 1 week"

    # Keep summary deterministic and fast; avoid LLM latency for log flow.
    summary = text[:220] if len(text) > 220 else text
    
    # Return structured data (database save will be done by route handler)
    result = {
        "status": "extracted",
        "data": {
            "doctor_name": extracted_doctor,
            "summary": summary,
            "sentiment": sentiment,
            "follow_up": follow_up,
            "interaction_text": interaction_text
        }
    }
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    print(f"[DEBUG][TOOL] log_interaction_tool end elapsed_ms={elapsed_ms}")
    return result


def summarize_interaction_tool(interaction_text: str) -> dict:
    """
    Converts long interaction text into a concise CRM summary.
    Uses LLM for intelligent summarization.
    """
    
    summarize_prompt = f"""
    Create a concise 2-3 sentence CRM summary of this interaction:
    
    {interaction_text}
    
    The summary should capture the key discussion points and outcomes.
    """
    
    response = llm.invoke(summarize_prompt)
    
    return {
        "status": "summarized",
        "summary": response.content
    }


def suggest_next_action_tool(interaction_id: int, context: Optional[str] = None, db_session: Session = None) -> dict:
    """
    Suggests next steps for follow-up based on interaction history.
    Uses LLM to provide intelligent recommendations.
    """
    
    if db_session:
        interaction = db_session.query(Interaction).filter(
            Interaction.id == interaction_id
        ).first()
        
        if not interaction:
            return {"status": "error", "message": "Interaction not found"}
        
        interaction_summary = f"Doctor: {interaction.doctor_name}, Summary: {interaction.summary}"
    else:
        interaction_summary = f"Interaction ID: {interaction_id}"
    
    suggestion_prompt = f"""
    Based on this HCP interaction, what are the best next steps for follow-up?
    
    {interaction_summary}
    {f'Additional context: {context}' if context else ''}
    
    Provide 2-3 actionable next steps for the sales rep.
    """
    
    response = llm.invoke(suggestion_prompt)
    
    return {
        "status": "suggested",
        "next_actions": response.content
    }


def fetch_interaction_tool(doctor_name: Optional[str] = None, limit: int = 10, db_session: Session = None) -> dict:
    """
    Retrieves interactions filtered by doctor name or recent.
    """
    
    if not db_session:
        return {"status": "error", "message": "Database session not available"}
    
    query = db_session.query(Interaction)
    
    if doctor_name:
        query = query.filter(Interaction.doctor_name.ilike(f"%{doctor_name}%"))
    
    # Order by most recent first
    interactions = query.order_by(Interaction.created_at.desc()).limit(limit).all()
    
    return {
        "status": "fetched",
        "count": len(interactions),
        "interactions": [
            {
                "id": i.id,
                "doctor_name": i.doctor_name,
                "summary": i.summary,
                "sentiment": i.sentiment,
                "follow_up": i.follow_up,
                "interaction_text": i.interaction_text,
                "created_at": i.created_at.isoformat()
            }
            for i in interactions
        ]
    }


def edit_interaction_tool(interaction_id: int, field: str, new_value: str, db_session: Session = None) -> dict:
    """
    Edits an existing interaction field.
    Validates field name and updates database.
    """
    
    if not db_session:
        return {"status": "error", "message": "Database session not available"}
    
    allowed_fields = ["summary", "sentiment", "follow_up", "doctor_name"]
    
    if field not in allowed_fields:
        return {
            "status": "error",
            "message": f"Field '{field}' not editable. Allowed: {allowed_fields}"
        }
    
    interaction = db_session.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    
    if not interaction:
        return {"status": "error", "message": "Interaction not found"}
    
    # Update field
    setattr(interaction, field, new_value)
    db_session.commit()
    
    return {
        "status": "updated",
        "message": f"Updated {field} for interaction {interaction_id}",
        "interaction_id": interaction_id
    }
