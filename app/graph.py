from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agents.segregator import segregate_pages
from app.agents.id_agent import extract_id_details
from app.agents.discharge_agent import extract_discharge_details
from app.agents.bill_agent import extract_bill_details
from app.agents.aggregator import aggregate_results


class ClaimState(TypedDict, total=False):
    claim_id: str
    pages: list[dict]
    classifications: list[dict]
    id_result: dict
    discharge_result: dict
    bill_result: dict
    final_result: dict


def segregator_node(state: ClaimState):
    classifications = segregate_pages(state["pages"])
    return {"classifications": classifications}


def id_agent_node(state: ClaimState):
    relevant_pages = []

    category_by_page = {
        item["page_number"]: item["category"]
        for item in state["classifications"]
    }

    for page in state["pages"]:
        category = category_by_page[page["page_number"]]
        text = page["text"].lower()

        is_identity_or_claim = category in [
            "identity_document",
            "claim_forms"
        ]

        is_insurance_document = (
            category == "other"
            and any(word in text for word in [
                "insurance",
                "policy number",
                "member id",
                "policy holder"
            ])
        )

        if is_identity_or_claim or is_insurance_document:
            relevant_pages.append(page)

    result = extract_id_details(relevant_pages)
    return {"id_result": result}


def discharge_agent_node(state: ClaimState):
    relevant_pages = [
        page for page in state["pages"]
        if any(
            item["page_number"] == page["page_number"]
            and item["category"] == "discharge_summary"
            for item in state["classifications"]
        )
    ]

    result = extract_discharge_details(relevant_pages)
    return {"discharge_result": result}


def bill_agent_node(state: ClaimState):
    relevant_pages = [
        page for page in state["pages"]
        if any(
            item["page_number"] == page["page_number"]
            and item["category"] == "itemized_bill"
            for item in state["classifications"]
        )
    ]

    result = extract_bill_details(relevant_pages)
    return {"bill_result": result}


def aggregator_node(state: ClaimState):
    result = aggregate_results(state)
    return {"final_result": result}


builder = StateGraph(ClaimState)

builder.add_node("segregator", segregator_node)
builder.add_node("id_agent", id_agent_node)
builder.add_node("discharge_agent", discharge_agent_node)
builder.add_node("bill_agent", bill_agent_node)
builder.add_node("aggregator", aggregator_node)

builder.add_edge(START, "segregator")

# Run the three extraction agents after classification.
builder.add_edge("segregator", "id_agent")
builder.add_edge("segregator", "discharge_agent")
builder.add_edge("segregator", "bill_agent")

# Wait until all three extraction agents finish.
builder.add_edge(
    ["id_agent", "discharge_agent", "bill_agent"],
    "aggregator"
)

builder.add_edge("aggregator", END)

claim_graph = builder.compile()
