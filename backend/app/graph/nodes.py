from app.agents.planner import PlannerAgent

planner = PlannerAgent()


def planner_node(state):

    state["plan"] = planner.execute(
        state["user_prompt"],
        state.get("generation_level")
    )

    return state