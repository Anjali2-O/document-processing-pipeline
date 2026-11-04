def aggregate_results(state: dict) -> dict:
    return {
        "claim_id": state["claim_id"],
        "classifications": state["classifications"],
        "patient_details": state.get("id_result", {}),
        "discharge_details": state.get("discharge_result", {}),
        "bill_details": state.get("bill_result", {})
    }
