

import json
from agent import get_document_claims, get_document_totals, inspect_pages, interact, validate_totals


def evaluate_and_tool_call_loop(file_path):
    prompt = f"""
    You must extract data from an insurance loss run file titled '{file_path}'. 
    
    Required fields: total_claim_count, total_open_count, total_paid_amount, total_reserve, total_incurred (dollar amounts as floats)

    Use your tools in whatever order is most appropriate for the document. You are free to explore the document, inspect suspicious sections, and decide which steps are necessary to reach a complete result.

    Do not stop until the extraction is complete and validation is satisfied.
    If validation reveals a mismatch, continue investigating. Depending on the document, useful next steps may include:
    - Re-examining pages where claims may be missing
    - Re-running extraction on specific page ranges that need closer review
    - Checking whether claim information is distributed across multiple tables or sections
    - Inspecting headers, subtotals, and section transitions that may affect claim grouping

    A complete extraction is more important than a fast but partial result.
    """

    history = [
            {
            "type": "user_input",
            "content": [prompt]
        }
    ]

    interaction = interact(prompt)

    while True:
        for step in interaction.steps:
            history.append(step.model_dump())

        fc_step = next(s for s in interaction.steps if s.type == "function_call")
        if fc_step.name == "extract_claims_declaration":
            result = get_document_claims(**fc_step.arguments)
        elif fc_step.name == "focus_pages_declaration":
            result = inspect_pages(**fc_step.arguments)
        elif fc_step.name == "get_document_claims":
            result = get_document_totals(**fc_step.arguments)
        elif fc_step.name == "validate_totals":
            result = validate_totals(file_path, **fc_step.arguments)
        elif fc_step.name == "return_validated_results_declaration":
            return ""
        
        history.append({
            "type": "function_result",
            "name": fc_step.name,
            "call_id": fc_step.id,
            "result": [{"type": "text", "text": json.dumps(result)}],
        })

        interaction = interact(history)

