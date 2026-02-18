from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph

# Absolute imports (since we run from backend folder)
from agents.classification_agent import classification_agent
from agents.icp_agent import icp_agent
from agents.platform_agent import platform_decision_agent
from agents.linkedin_agent import linkedin_agent
from agents.email_agent import email_agent
from agents.call_agent import call_agent


# ---------------------------
# State Definition
# ---------------------------

class AgentState(TypedDict, total=False):
    user_input: str
    classification: dict
    icp_rankings: List[Dict]
    selected_channel: str
    generated_content: Dict


# ---------------------------
# Create Graph
# ---------------------------

graph = StateGraph(AgentState)

# Core Agents
graph.add_node("classification", classification_agent)
graph.add_node("icp", icp_agent)
graph.add_node("platform", platform_decision_agent)

# Channel Agents
graph.add_node("linkedin", linkedin_agent)
graph.add_node("email", email_agent)
graph.add_node("call", call_agent)


# ---------------------------
# Entry Point
# ---------------------------

graph.set_entry_point("classification")


# ---------------------------
# Core Flow
# ---------------------------

graph.add_edge("classification", "icp")
graph.add_edge("icp", "platform")


# ---------------------------
# Conditional Routing
# ---------------------------

def route_channel(state: AgentState):
    channel = state.get("selected_channel", "LinkedIn")

    if channel == "LinkedIn":
        return "linkedin"
    elif channel == "Email":
        return "email"
    else:
        return "call"


graph.add_conditional_edges(
    "platform",
    route_channel,
    {
        "linkedin": "linkedin",
        "email": "email",
        "call": "call"
    }
)


# ---------------------------
# Finish Points
# ---------------------------

graph.set_finish_point("linkedin")
graph.set_finish_point("email")
graph.set_finish_point("call")


# ---------------------------
# Compile Graph
# ---------------------------

app = graph.compile()
