"""
LangGraph Agent Workflow - Core AI orchestration engine.
Uses LangGraph for state management and conditional routing to tools.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
import json
import config
from sqlalchemy.orm import Session
from langgraph.prebuilt import ToolNode

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


# Initialize LLM
llm = ChatGroq(
    temperature=0.7,
    model_name=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY
)


def extract_doctor_name_from_text(text: str) -> str:
    """Extract doctor name from user text using LLM."""
    prompt = f"Extract the doctor's name from this text. If no doctor is mentioned, return null. Text: '{text}'"
    response = llm.invoke(prompt)
    doctor_name = response.content.strip()
    return doctor_name if doctor_name.lower() != "null" and doctor_name else None


def extract_interaction_id_from_text(text: str) -> int:
    """Extract interaction ID from user text using LLM."""
    prompt = f"Extract the interaction ID (number) from this text. If no ID is mentioned, return null. Text: '{text}'"
    response = llm.invoke(prompt)
    try:
        interaction_id = int(response.content.strip())
        return interaction_id
    except (ValueError, AttributeError):
        return None


def extract_edit_params_from_text(text: str) -> dict:
    """Extract edit parameters from user text using LLM."""
    prompt = f"""
    Extract edit parameters from this text. Look for:
    - interaction_id: the ID number of the interaction to edit
    - field: what to edit (summary, sentiment, follow_up, doctor_name)
    - new_value: the new value to set
    
    Text: "{text}"
    
    Return as JSON: {{"interaction_id": number, "field": "field_name", "new_value": "new value"}}
    If parameters are incomplete, return null.
    """
    response = llm.invoke(prompt)
    try:
        params = json.loads(response.content)
        if all(k in params for k in ["interaction_id", "field", "new_value"]):
            return params
    except:
        pass
    return None


def route_agent(state: AgentState) -> str:
    """
    Router function: determines next node based on agent decision.
    Routes to tool_node if a tool is selected, otherwise returns END.
    """
    if state.get("selected_tool"):
        return "tool_node"
    return END


def agent_node(state: AgentState) -> AgentState:
    """
    Main agent reasoning node.
    - Analyzes user message
    - Decides which tool to use
    - Routes appropriately
    """
    
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
    
    Always respond conversationally and confirm tool usage.
    """
    
    # Get the last user message
    last_message = state["messages"][-1]
    user_input = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # Create reasoning prompt
    reasoning_prompt = f"""
    User request: "{user_input}"
    
    Analyze this request and decide:
    1. What is the user trying to do?
    2. Which tool should be used?
    3. What parameters are needed?
    
    Respond in this JSON format (NO MARKDOWN):
    {{
        "intent": "description of what user wants",
        "selected_tool": "tool_name or null",
        "parameters": {{}},
        "conversational_response": "Your response to the user"
    }}
    """
    
    # Get agent's decision
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=reasoning_prompt)
    ]
    
    response = llm.invoke(messages)
    
    try:
        # Parse agent decision
        decision = json.loads(response.content)
        selected_tool = decision.get("selected_tool")
        if not selected_tool or selected_tool == "null":
            selected_tool = "none"
        ai_response = decision.get("conversational_response", "Processing your request...")
    except json.JSONDecodeError:
        # Fallback parsing
        selected_tool = None
        ai_response = response.content
    
    # Update state
    state["selected_tool"] = selected_tool
    state["messages"].append(AIMessage(content=ai_response))
    
    return state


def tool_node(state: AgentState) -> AgentState:
    """
    Executes selected tool and returns result.
    Tool execution with database session context.
    """
    
    selected_tool = state.get("selected_tool")
    
    if not selected_tool:
        return state
    
    db_session = state.get("db_session")
    last_message = state["messages"][-2]  # Get user message (before AI response)
    user_input = last_message.content
    
    tool_result = None
    
    try:
        # Route to appropriate tool
        if selected_tool == "log_interaction_tool":
            # Extract information from user message
            tool_result = log_interaction_tool(
                doctor_name="",
                interaction_text=user_input,
            )
        
        elif selected_tool == "summarize_interaction_tool":
            tool_result = summarize_interaction_tool(
                interaction_text=user_input
            )
        
        elif selected_tool == "fetch_interaction_tool":
            # Try to extract doctor name from user message
            doctor_name = extract_doctor_name_from_text(user_input)
            tool_result = fetch_interaction_tool(
                doctor_name=doctor_name,
                limit=10,
                db_session=db_session
            )
        
        elif selected_tool == "suggest_next_action_tool":
            # Try to extract interaction_id from user message
            interaction_id = extract_interaction_id_from_text(user_input)
            if interaction_id:
                tool_result = suggest_next_action_tool(
                    interaction_id=interaction_id,
                    context=user_input,
                    db_session=db_session
                )
            else:
                tool_result = {"status": "info", "message": "Please specify which interaction ID you'd like suggestions for"}
        
        elif selected_tool == "edit_interaction_tool":
            # Try to extract edit parameters from user message
            edit_params = extract_edit_params_from_text(user_input)
            if edit_params:
                tool_result = edit_interaction_tool(
                    interaction_id=edit_params["interaction_id"],
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
    
    state["tool_result"] = tool_result
    
    # Add tool result to messages
    tool_message = f"Tool '{selected_tool}' executed. Result: {json.dumps(tool_result)}"
    state["messages"].append(HumanMessage(content=tool_message))
    
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
    
    # Tool node loops back to agent
    workflow.add_edge("tool_node", "agent")
    
    # Compile graph
    return workflow.compile()


# Create agent graph
agent_graph = build_agent_graph()


def run_agent(user_message: str, db_session: Session) -> dict:
    """
    Run the agent with user input and return response.
    
    Args:
        user_message: User's chat message
        db_session: Database session for tool execution
    
    Returns:
        Dictionary with AI response and structured data
    """
    
    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=user_message)],
        "db_session": db_session,
        "selected_tool": None,
        "tool_result": None
    }
    
    # Run agent
    final_state = agent_graph.invoke(initial_state)
    
    # Extract response
    ai_message = None
    tool_used = final_state.get("selected_tool", "reasoning")
    tool_result = final_state.get("tool_result", {})
    
    # Get last AI message
    for message in reversed(final_state["messages"]):
        if isinstance(message, AIMessage):
            ai_message = message.content
            break
    
    return {
        "ai_message": ai_message or "I'm ready to help with your CRM needs.",
        "structured_data": tool_result,
        "tool_used": tool_used
    }
