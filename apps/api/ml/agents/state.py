from typing import TypedDict


class AgentState(TypedDict):
    asset_id: str
    org_id: str
    search_tasks: list[dict]
    discovered_urls: list[str]
    candidate_matches: list[dict]
    confirmed_violations: list[dict]
    errors: list[dict]
    status: str