"""
LangGraph Agent Workflow - Core AI orchestration engine.
Uses LangGraph for state management and conditional routing to tools.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json
import re
from time import perf_counter
import config
from sqlalchemy.orm import Session
from models.database import Interaction

# Import tools
from .tools import (
    log_interaction_tool,
    summarize_interaction_tool,
    suggest_next_action_tool,
    fetch_interaction_tool,
    edit_interaction_tool
)


# Define agent state
class AgentState(TypedDict):
    """State schema for LangGraph agent."""
    messages: Annotated[Sequence, add_messages]
    db_session: Session  # Passed through for tool execution
    selected_tool: str
    tool_result: dict
    tool_params: dict


# Initialize LLM
llm = ChatGroq(
    temperature=0.0,
    model_name=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY
)

VALID_TOOLS = {
    "log_interaction_tool",
    "summarize_interaction_tool",
    "suggest_next_action_tool",
    "fetch_interaction_tool",
    "edit_interaction_tool",
}


def _heuristic_route(user_input: str) -> tuple[str, dict, str] | None:
    """Fast deterministic routing to avoid extra LLM call on common intents."""
    text = user_input.lower()
    compact = re.sub(r"[^a-z0-9\s]", " ", text)
    wants_fetch = (
        re.search(r"\b(list|fetch|show)\b.*\b(all|every|the\s+)?interac", compact)
        or re.search(r"\bget\b.*\b(all\s+)?interac", compact)
        or "all interactions" in compact
        or "all interaction records" in compact
        or "interacctions" in compact
        or re.search(r"\bgive me (all )?details\b", compact)
        or re.search(r"\bfull details\b", compact)
    )
    if wants_fetch and not re.search(r"\bsummaris|\bsummariz|concise summaries|summary\b", compact):
        return ("fetch_interaction_tool", {"limit": 50}, "Fetching interactions now.")
    if compact.strip() in {"summarize text", "summarise text"}:
        return (
            "",
            {},
            'Paste the interaction text to summarize, or say e.g. "summarize interaction 2".',
        )
    if re.search(r"summaris|summariz|summary of|concise summaries|tl\s*dr", compact):
        iid = extract_interaction_id_from_text(user_input)
        params: dict = {"interaction_text": user_input}
        if iid is not None:
            params["interaction_id"] = iid
        return ("summarize_interaction_tool", params, "Summarizing the interaction.")
    if any(word in text for word in ["suggest", "next action", "follow-up strategy", "follow up strategy"]):
        iid = extract_interaction_id_from_text(user_input)
        params = {"context": user_input}
        if iid is not None:
            params["interaction_id"] = iid
        return ("suggest_next_action_tool", params, "Analyzing and suggesting next steps.")
    if any(word in text for word in ["edit", "update", "change"]):
        return ("edit_interaction_tool", {}, "Updating interaction details.")
    if any(word in text for word in ["save", "log", "met dr", "i met dr", "doctor", "dr."]):
        return (
            "log_interaction_tool",
            {"doctor_name": extract_doctor_name_from_text(user_input) or "", "interaction_text": user_input},
            "Got it. Saving this interaction now.",
        )
    if compact.strip() in {"yes", "yeah", "yep", "ok", "okay"}:
        return ("", {}, "Please share interaction details (doctor, discussion, sentiment, follow-up) and I will save it immediately.")
    return None


def extract_doctor_name_from_text(text: str) -> str | None:
    """Extract doctor name from user text using regex (fast path)."""
    match = re.search(r"\b(?:dr\.?|doctor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", text)
    return f"Dr. {match.group(1)}" if match else None


def extract_interaction_id_from_text(text: str) -> int | None:
    """Extract interaction ID from user text using regex (fast path)."""
    patterns = (
        r"\b(?:interaction|interation)\s*(?:number|num|no\.?)?\s*[:#]?\s*(\d+)\b",
        r"\b(?:interaction|interation)\s+(\d+)\b",
        r"\b(?:id|interaction)\s*[:#]\s*(\d+)\b",
        r"\b(?:id)\s+(?:of|for)\s+interaction\s+(?:number\s+)?(\d+)\b",
    )
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    match = re.search(r"\b(?:id|interaction)\s*[:#]?\s*(\d+)\b", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def extract_edit_params_from_text(text: str) -> dict | None:
    """Extract edit parameters from user text using regex (fast path)."""
    interaction_id = extract_interaction_id_from_text(text)

    field = None
    field_synonyms = (
        ("doctor_name", r"\b(professional name|doctor name|doctor|hcp name|physician)\b"),
        ("summary", r"\bsummary\b"),
        ("sentiment", r"\bsentiment\b"),
        ("follow_up", r"\b(follow\s*[\s-]?up|followup)\b"),
    )
    for fname, rx in field_synonyms:
        if re.search(rx, text, re.IGNORECASE):
            field = fname
            break

    new_value = None
    quoted = re.search(r"(?:to|as)\s+\"([^\"]+)\"", text, re.IGNORECASE)
    from_to = re.search(
        r"\bfrom\s+[^t]+\s+to\s+(.+?)(?:\.|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    as_plain = re.search(
        r"\b(?:to|as)\s+([^\n,.]+?)(?:\s*(?:\.|$)|$)",
        text,
        re.IGNORECASE,
    )
    if quoted:
        new_value = quoted.group(1).strip()
    elif from_to:
        new_value = from_to.group(1).strip().strip('"').strip("'")
    elif as_plain:
        new_value = as_plain.group(1).strip().strip('"').strip("'")

    if interaction_id and field and new_value:
        return {"interaction_id": interaction_id, "field": field, "new_value": new_value}
    return None


def route_agent(state: AgentState) -> str:
    """
    Router function: determines next node based on agent decision.
    Routes to tool_node if a tool is selected, otherwise returns END.
    """
    if state.get("selected_tool") in VALID_TOOLS:
        return "tool_node"
    return END


def agent_node(state: AgentState) -> AgentState:
    """
    Main agent reasoning node.
    - Analyzes user message
    - Decides which tool to use
    - Routes appropriately
    """
    
    started_at = perf_counter()
    print("[DEBUG][AGENT] agent_node start")
    # System prompt for agent
    system_prompt = """
    You are an intelligent CRM assistant for healthcare interactions.
    Your role is to help sales representatives log and manage interactions with Healthcare Professionals (HCPs).
    
    You have access to these tools:
    1. log_interaction_tool - Extract and save new HCP interactions
    2. summarize_interaction_tool - Create concise summaries
    3. suggest_next_action_tool - Suggest follow-up actions
    4. fetch_interaction_tool - Retrieve past interactions
    5. edit_interaction_tool - Modify existing interactions
    
    For each user request:
    - Understand the intent
    - Select the most appropriate tool
    - Prepare the required parameters
    
    When the user provides interaction details, use log_interaction_tool.
    When asking about past interactions, use fetch_interaction_tool.
    When editing details, use edit_interaction_tool.
    When requesting suggestions, use suggest_next_action_tool.
    
    Do not ask for confirmation if enough details are already present.
    If user asks to save/log an interaction and details are present, execute immediately.
    Always respond conversationally and action-oriented.
    Return strict JSON only (no markdown).
    """
    
    # Get the last user message
    last_message = state["messages"][-1]
    user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    heuristic = _heuristic_route(user_input)
    if heuristic:
        selected_tool, tool_params, ai_response = heuristic
        state["selected_tool"] = selected_tool
        state["tool_params"] = tool_params
        state["messages"].append(AIMessage(content=ai_response))
        elapsed_ms = int((perf_counter() - started_at) * 1000)
        print(f"[DEBUG][AGENT] agent_node heuristic selected_tool='{selected_tool}' elapsed_ms={elapsed_ms}")
        return state

    # Avoid LLM fallback to keep response latency stable.
    selected_tool = ""
    tool_params = {}
    ai_response = (
        "Please provide a clear CRM action: save/log interaction, list interactions, "
        "summarize text, suggest next action, or edit an interaction."
    )
    
    # Update state
    state["selected_tool"] = selected_tool
    state["tool_params"] = tool_params
    state["messages"].append(AIMessage(content=ai_response))
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    print(f"[DEBUG][AGENT] agent_node end selected_tool='{selected_tool or 'reasoning'}' elapsed_ms={elapsed_ms}")
    return state


def tool_node(state: AgentState) -> AgentState:
    """
    Executes selected tool and returns result.
    Tool execution with database session context.
    """
    
    started_at = perf_counter()
    selected_tool = state.get("selected_tool")
    if selected_tool not in VALID_TOOLS:
        return state

    print(f"[DEBUG][AGENT] tool_node start selected_tool='{selected_tool}'")
    db_session = state.get("db_session")
    user_input = state["messages"][0].content
    tool_params = state.get("tool_params", {}) or {}

    tool_result = None
    
    try:
        # Route to appropriate tool
        if selected_tool == "log_interaction_tool":
            tool_result = log_interaction_tool(
                doctor_name=tool_params.get("doctor_name", ""),
                interaction_text=tool_params.get("interaction_text", user_input),
                db_session=db_session,
            )
        
        elif selected_tool == "summarize_interaction_tool":
            iid = tool_params.get("interaction_id")
            text_to_summarize = tool_params.get("interaction_text", user_input)
            if iid and db_session:
                row = (
                    db_session.query(Interaction)
                    .filter(Interaction.id == int(iid))
                    .first()
                )
                if row:
                    text_to_summarize = row.interaction_text or row.summary or ""
                else:
                    tool_result = {"status": "error", "message": f"Interaction {iid} not found"}
                    state["tool_result"] = tool_result
                    elapsed_ms = int((perf_counter() - started_at) * 1000)
                    print(f"[DEBUG][AGENT] tool_node end selected_tool='{selected_tool}' elapsed_ms={elapsed_ms}")
                    return state
            if not str(text_to_summarize).strip():
                tool_result = {
                    "status": "info",
                    "message": "Paste interaction text or specify an interaction ID to summarize.",
                }
            else:
                tool_result = summarize_interaction_tool(interaction_text=text_to_summarize)
        
        elif selected_tool == "fetch_interaction_tool":
            doctor_name = tool_params.get("doctor_name") or extract_doctor_name_from_text(user_input)
            tool_result = fetch_interaction_tool(
                doctor_name=doctor_name,
                limit=int(tool_params.get("limit", 10)),
                db_session=db_session
            )
        
        elif selected_tool == "suggest_next_action_tool":
            interaction_id = tool_params.get("interaction_id") or extract_interaction_id_from_text(user_input)
            if not interaction_id and db_session:
                latest = (
                    db_session.query(Interaction)
                    .order_by(Interaction.created_at.desc())
                    .first()
                )
                if latest:
                    interaction_id = latest.id
            if interaction_id:
                tool_result = suggest_next_action_tool(
                    interaction_id=int(interaction_id),
                    context=tool_params.get("context", user_input),
                    db_session=db_session
                )
            else:
                tool_result = {
                    "status": "info",
                    "message": "No interactions found yet. Log an interaction first, or specify an interaction ID.",
                }
        
        elif selected_tool == "edit_interaction_tool":
            edit_params = {
                "interaction_id": tool_params.get("interaction_id"),
                "field": tool_params.get("field"),
                "new_value": tool_params.get("new_value"),
            }
            if not all(edit_params.values()):
                edit_params = extract_edit_params_from_text(user_input)
            if edit_params:
                tool_result = edit_interaction_tool(
                    interaction_id=int(edit_params["interaction_id"]),
                    field=edit_params["field"],
                    new_value=edit_params["new_value"],
                    db_session=db_session
                )
            else:
                tool_result = {"status": "info", "message": "Please specify what to edit: interaction ID, field, and new value"}
    
    except Exception as e:
        tool_result = {
            "status": "error",
            "message": f"Tool execution error: {str(e)}"
        }

    if not isinstance(tool_result, dict):
        tool_result = {"status": "error", "message": "Tool returned invalid result format"}

    state["tool_result"] = tool_result
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    print(f"[DEBUG][AGENT] tool_node end selected_tool='{selected_tool}' elapsed_ms={elapsed_ms}")
    return state


def build_agent_graph():
    """
    Builds and compiles the LangGraph workflow.
    """
    
    # Create workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tool_node", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        route_agent,
        {
            "tool_node": "tool_node",
            END: END
        }
    )
    
    # Finish after one tool execution to avoid agent/tool loops.
    workflow.add_edge("tool_node", END)
    
    # Compile graph
    return workflow.compile()


# Create agent graph
agent_graph = build_agent_graph()


def _format_fetch_ai_message(tool_result: dict) -> str:
    if tool_result.get("status") != "fetched":
        return tool_result.get("message", "Could not fetch interactions.")
    rows = tool_result.get("interactions") or []
    n = len(rows)
    if n == 0:
        return "No interactions matched your query."
    parts = [f"Found {n} interaction(s). Full records:"]
    for r in rows:
        tid = r.get("id")
        doc = r.get("doctor_name")
        sent = r.get("sentiment")
        fu = r.get("follow_up") or "—"
        summ = (r.get("summary") or "")[:200]
        raw = (r.get("interaction_text") or "")[:400]
        parts.append(
            f"\n— ID {tid} | {doc} | sentiment: {sent} | follow-up: {fu}\n"
            f"  summary: {summ}\n"
            f"  notes: {raw}{'…' if len(r.get('interaction_text') or '') > 400 else ''}"
        )
    return "\n".join(parts)


def run_agent(user_message: str, db_session: Session) -> dict:
    """
    Run the agent with user input and return response.
    
    Args:
        user_message: User's chat message
        db_session: Database session for tool execution
    
    Returns:
        Dictionary with AI response and structured data
    """
    
    started_at = perf_counter()
    print("[DEBUG][AGENT] run_agent start")
    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "db_session": db_session,
        "selected_tool": "",
        "tool_result": {},
        "tool_params": {}
    }
    
    # Run agent
    final_state = agent_graph.invoke(initial_state)
    
    # Extract response
    ai_message = None
    tool_used = final_state.get("selected_tool") or "reasoning"
    if not isinstance(tool_used, str):
        tool_used = "reasoning"
    tool_result = final_state.get("tool_result") or {}
    if not isinstance(tool_result, dict):
        tool_result = {"status": "error", "message": "Invalid tool result format"}
    
    # Get last AI message
    for message in reversed(final_state["messages"]):
        if isinstance(message, AIMessage):
            ai_message = message.content
            break
    
    if tool_used == "log_interaction_tool" and tool_result.get("status") == "extracted":
        ai_message = "Interaction details extracted successfully. Saving now."
    elif tool_used == "fetch_interaction_tool":
        ai_message = _format_fetch_ai_message(tool_result)
    elif tool_used == "summarize_interaction_tool" and tool_result.get("status") == "summarized":
        ai_message = tool_result.get("summary") or ai_message
    elif tool_used == "suggest_next_action_tool" and tool_result.get("status") == "suggested":
        ai_message = tool_result.get("next_actions") or ai_message
    elif tool_used == "suggest_next_action_tool" and tool_result.get("status") == "info":
        ai_message = tool_result.get("message") or ai_message
    elif tool_used == "summarize_interaction_tool" and tool_result.get("status") == "info":
        ai_message = tool_result.get("message") or ai_message
    elif tool_result.get("status") == "error":
        ai_message = tool_result.get("message", "Something went wrong while processing the request.")

    result = {
        "ai_message": ai_message or "I'm ready to help with your CRM needs.",
        "structured_data": tool_result,
        "tool_used": tool_used
    }
    elapsed_ms = int((perf_counter() - started_at) * 1000)
    print(f"[DEBUG][AGENT] run_agent end tool_used='{tool_used}' elapsed_ms={elapsed_ms}")
    return result
