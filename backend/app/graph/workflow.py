from langgraph.graph import StateGraph, END

from app.graph.state import WebsiteState
from app.graph.nodes import planner_node

builder = StateGraph(WebsiteState)

builder.add_node("planner", planner_node)

builder.set_entry_point("planner")

builder.add_edge("planner", END)

graph = builder.compile()