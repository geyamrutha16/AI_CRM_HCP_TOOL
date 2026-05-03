"""
Pydantic schemas for request/response validation.
Ensures type safety and API documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class InteractionBase(BaseModel):
    """Base schema for interaction data."""
    doctor_name: str = Field(..., min_length=1, description="Name of the healthcare professional")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    sentiment: str = Field("neutral", description="Sentiment: positive/neutral/negative")
    follow_up: Optional[str] = Field(None, description="Follow-up notes or date")
    interaction_text: str = Field(..., description="Raw interaction text")


class InteractionCreate(InteractionBase):
    """Schema for creating interactions."""
    pass


class InteractionUpdate(BaseModel):
    """Schema for updating interactions."""
    doctor_name: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    follow_up: Optional[str] = None
    interaction_text: Optional[str] = None


class InteractionResponse(InteractionBase):
    """Schema for interaction responses."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentRequest(BaseModel):
    """Schema for agent execution requests."""
    message: str = Field(..., description="User message to process")
    interaction_id: Optional[int] = Field(None, description="Existing interaction ID to edit")


class AgentResponse(BaseModel):
    """Schema for agent execution responses."""
    ai_message: str = Field(..., description="AI response message")
    structured_data: dict = Field(..., description="Extracted structured data")
    tool_used: str = Field(..., description="Tool called by agent")
    interaction_id: Optional[int] = Field(None, description="Created/updated interaction ID")


class VoiceTranscriptionRequest(BaseModel):
    """Schema for voice transcription requests."""
    audio_base64: str = Field(..., description="Base64 encoded audio")
    format: str = Field("wav", description="Audio format")


class SentimentAnalysis(BaseModel):
    """Schema for sentiment analysis results."""
    text: str
    sentiment: str
    confidence: float = Field(default=0.85)
