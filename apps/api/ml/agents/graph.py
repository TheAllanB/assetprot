from langgraph.graph import END, StateGraph

from ml.agents.state import AgentState
from ml.agents.planner_agent import planner_node
from ml.agents.crawler_agent import crawler_node
from ml.agents.matcher_agent import matcher_node
from ml.agents.watermark_decoder_node import watermark_decoder_node
from ml.agents.reporter_node import reporter_node


def create_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("crawler", crawler_node)
    workflow.add_node("matcher", matcher_node)
    workflow.add_node("watermark_decoder", watermark_decoder_node)
    workflow.add_node("reporter", reporter_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "crawler")
    workflow.add_edge("crawler", "matcher")
    workflow.add_edge("matcher", "watermark_decoder")
    workflow.add_edge("watermark_decoder", "reporter")
    workflow.add_edge("reporter", END)

    return workflow.compile()


agent_graph = create_agent_graph()