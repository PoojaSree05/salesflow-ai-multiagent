"""
Multi-Agent System Workflow – Assessment Task 2 Architecture

Flow: User Input → A1 Classification → A2 ICP → A3 Platform Decision → A4 Content Generation
Output: Content delivered via LinkedIn (A4), Email (A5), or Call (A6) channel
"""

from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph

from agents.classification_agent import classification_agent
from agents.icp_agent import icp_agent
from agents.platform_agent import platform_decision_agent
from agents.content_agent import content_generation_agent


# ---------------------------
# State Definition
# ---------------------------

class AgentState(TypedDict, total=False):
    user_input: str
    classification: dict
    icp_rankings: List[Dict]
    selected_channel: str
    channel_reasoning: str
    generated_content: Dict


# ---------------------------
# Create Graph
# ---------------------------

graph = StateGraph(AgentState)

# A1 – Classification Agent
graph.add_node("classification", classification_agent)

# A2 – ICP Module (Ideal Customer Profile)
graph.add_node("icp", icp_agent)

# A3 – Platform Decision Agent
graph.add_node("platform", platform_decision_agent)

# A4 – Content Generation Agent (produces content for selected channel)
graph.add_node("content", content_generation_agent)


# ---------------------------
# Linear Flow: A1 → A2 → A3 → A4
# ---------------------------

graph.set_entry_point("classification")
graph.add_edge("classification", "icp")
graph.add_edge("icp", "platform")
graph.add_edge("platform", "content")
graph.set_finish_point("content")


# ---------------------------
# Compile
# ---------------------------

app = graph.compile()
