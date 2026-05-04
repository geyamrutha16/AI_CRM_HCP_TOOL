"""
FastAPI routes for AI agent operations.
Handles chat-based interaction logging through LangGraph agent.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import Interaction, get_db
from models.schemas import AgentRequest, AgentResponse, InteractionCreate
from agents.agent import run_agent
import asyncio
import json
from time import perf_counter
import config

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentResponse)
async def run_agent_endpoint(
    request: AgentRequest,
    db: Session = Depends(get_db)
) -> AgentResponse:
    """
    Execute the AI agent with user message.
    
    - Processes user input through LangGraph agent
    - Calls appropriate tools based on agent decision
    - Saves interaction if extraction successful
    - Returns structured response
    
    Args:
        request: Agent request with user message
        db: Database session
    
    Returns:
        Agent response with AI message and structured data
    
    Raises:
        HTTPException: If agent execution fails
    """
    
    try:
        started_at = perf_counter()
        print("[DEBUG][API] /agent/run hit")
        # Run agent in thread with timeout so requests don't hang forever.
        agent_result = await asyncio.wait_for(
            asyncio.to_thread(run_agent, request.message, db),
            timeout=config.AGENT_TIMEOUT
        )
        
        # Extract structured data from tool result
        structured_data = agent_result.get("structured_data", {})
        tool_used = agent_result.get("tool_used") or "reasoning"
        if not isinstance(tool_used, str):
            tool_used = "reasoning"
        
        # If data extraction was successful, save to database
        interaction_id = None
        
        if tool_used == "log_interaction_tool" and structured_data.get("data"):
            extracted_data = structured_data["data"]
            
            # Create interaction record
            interaction = InteractionCreate(
                doctor_name=extracted_data.get("doctor_name", "Unknown"),
                summary=extracted_data.get("summary", ""),
                sentiment=extracted_data.get("sentiment", "neutral"),
                follow_up=extracted_data.get("follow_up", ""),
                interaction_text=extracted_data.get("interaction_text", "")
            )
            
            # Save to database
            db_interaction = Interaction(
                doctor_name=interaction.doctor_name,
                summary=interaction.summary,
                sentiment=interaction.sentiment,
                follow_up=interaction.follow_up,
                interaction_text=interaction.interaction_text
            )
            
            db.add(db_interaction)
            db.commit()
            db.refresh(db_interaction)
            print(f"[DEBUG][API] DB write success interaction_id={db_interaction.id}")
            
            interaction_id = db_interaction.id
        
        elapsed_ms = int((perf_counter() - started_at) * 1000)
        print(f"[DEBUG][API] /agent/run done tool_used='{tool_used}' elapsed_ms={elapsed_ms}")
        ai_message = agent_result.get("ai_message", "")
        if interaction_id:
            ai_message = f"Interaction saved successfully with ID #{interaction_id}."

        return AgentResponse(
            ai_message=ai_message,
            structured_data=structured_data,
            tool_used=tool_used,
            interaction_id=interaction_id
        )
    except asyncio.TimeoutError:
        return AgentResponse(
            ai_message="The AI service is taking longer than expected right now. Please retry in a moment.",
            structured_data={"status": "timeout", "message": "Agent execution timed out"},
            tool_used="reasoning",
            interaction_id=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")


@router.post("/analyze")
async def analyze_sentiment(
    text: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    Analyze sentiment of interaction text using LLM.
    
    Args:
        text: Text to analyze
        db: Database session
    
    Returns:
        Sentiment analysis results
    """
    
    try:
        # We can use the agent here too, or directly call LLM
        from langchain_groq import ChatGroq
        import config
        
        llm = ChatGroq(
            temperature=0.5,
            model_name=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY
        )
        
        sentiment_prompt = f"""
        Analyze the sentiment of this text and provide:
        1. Sentiment (positive/neutral/negative)
        2. Confidence score (0-1)
        3. Key emotions detected
        
        Text: "{text}"
        
        Return as JSON with keys: sentiment, confidence, emotions
        """
        
        response = llm.invoke(sentiment_prompt)
        
        try:
            result = json.loads(response.content)
        except:
            result = {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": ["neutral"]
            }
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis error: {str(e)}")


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for agent service.
    """
    return {
        "status": "healthy",
        "service": "langgraph-agent",
        "version": "1.0.0"
    }
