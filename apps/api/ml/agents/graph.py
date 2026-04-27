from langgraph.graph import END, StateGraph

from ml.agents.state import AgentState
from ml.agents import planner_agent, crawler_agent, matcher_agent, watermark_decoder_node, reporter_node


def create_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_agent.planner_node)
    workflow.add_node("crawler", crawler_agent.crawler_node)
    workflow.add_node("matcher", matcher_agent.matcher_node)
    workflow.add_node("watermark_decoder", watermark_decoder_node.watermark_decoder_node)
    workflow.add_node("reporter", reporter_node.reporter_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "crawler")
    workflow.add_edge("crawler", "matcher")
    workflow.add_edge("matcher", "watermark_decoder")
    workflow.add_edge("watermark_decoder", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()


agent_graph = create_agent_graph()