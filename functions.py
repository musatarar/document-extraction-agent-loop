from agent import get_document_claims, get_document_totals, inspect_pages
from models import CLAIM_RECORD_SCHEMA

# Gemini function declarations, each followed by the function it dispatches to.
# https://ai.google.dev/gemini-api/docs/function-calling
# Page numbers in declarations are 1-indexed; agent.py helpers take 0-indexed pages.


extract_claims_declaration = {
    "type": "function",
    "name": "extract_claims",
    "description": (
        "Extract claims from the document. Supports optional page ranges "
        "for iterative re-extraction of specific sections. Omit both page "
        "arguments to extract from the whole document."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "page_start": {
                "type": "integer",
                "description": "First page (1-indexed, inclusive) to extract from.",
            },
            "page_end": {
                "type": "integer",
                "description": "Last page (1-indexed, inclusive) to extract from.",
            },
        },
    },
}

def extract_claims(file_path: str, page_start: int | None = None, page_end: int | None = None) -> dict:
    pages = None
    if page_start is not None or page_end is not None:
        start = page_start or 1
        end = page_end or start
        pages = list(range(start - 1, end))
    return get_document_claims(file_path, pages=pages).model_dump()


focus_pages_declaration = {
    "type": "function",
    "name": "focus_pages",
    "description": (
        "Returns high-resolution PDF chunks of specific pages for detailed "
        "visual inspection."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "pages": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Page numbers (1-indexed) to return at high resolution.",
            },
            "prompt": {
                "type": "string",
                "description": "What to look for on these pages.",
            },
        },
        "required": ["pages"],
    },
}

def focus_pages(
    file_path: str,
    pages: list[int],
    prompt: str = "Describe all claims, subtotals, and totals on these pages in detail.",
) -> str:
    return inspect_pages(file_path, [p - 1 for p in pages], prompt)


validate_totals_declaration = {
    "type": "function",
    "name": "validate_totals",
    "description": (
        "Validates extracted claims against document totals. Checks financial "
        "totals AND claim count."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "claims": {
                "type": "array",
                "items": CLAIM_RECORD_SCHEMA,
                "description": "The extracted claim records to validate.",
            },
        },
        "required": ["claims"],
    },
}

def validate_totals(file_path: str, claims: list[dict], tolerance: float = 0.01) -> dict:
    """Compare extracted claims against the totals stated in the document.

    Checks claim count and paid/reserve/incurred sums. Totals the document does
    not state (None) are reported as unverified rather than failing validation.
    """
    doc_totals = get_document_totals(file_path)

    extracted = {
        "total_claims": len(claims),
        "total_paid": round(sum(c.get("total_paid") or 0 for c in claims), 2),
        "total_reserve": round(sum(c.get("total_reserve") or 0 for c in claims), 2),
        "total_incurred": round(sum(c.get("total_incurred") or 0 for c in claims), 2),
    }
    expected = {
        "total_claims": doc_totals.total_claims,
        "total_paid": doc_totals.total_paid,
        # Loss runs often label reserves as "outstanding"
        "total_reserve": doc_totals.total_reserve if doc_totals.total_reserve is not None else doc_totals.total_outstanding,
        "total_incurred": doc_totals.total_incurred,
    }

    checks = {}
    for field, actual in extracted.items():
        target = expected[field]
        if target is None:
            checks[field] = {"status": "unverified", "extracted": actual, "document": None}
            continue
        diff = round(actual - target, 2)
        ok = diff == 0 if field == "total_claims" else abs(diff) <= tolerance
        checks[field] = {"status": "match" if ok else "mismatch", "extracted": actual, "document": target, "difference": diff}

    # Claim numbers appearing more than once usually mean a page was extracted twice
    seen, duplicates = set(), set()
    for c in claims:
        num = c.get("claim_number")
        if num in seen:
            duplicates.add(num)
        seen.add(num)

    mismatches = [f for f, r in checks.items() if r["status"] == "mismatch"]
    return {
        "passed": not mismatches and not duplicates,
        "mismatches": mismatches,
        "duplicate_claim_numbers": sorted(duplicates),
        "open_claim_count": sum(1 for c in claims if (c.get("status") or "").strip().lower() in ("open", "reopened")),
        "checks": checks,
    }


return_validated_results_declaration = {
    "type": "function",
    "name": "return_validated_results",
    "description": (
        "Returns the final validated results once extracted claims reconcile "
        "with the document totals. Call this only after validation passes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "total_claim_count": {
                "type": "integer",
                "description": "Total number of claims in the document.",
            },
            "total_open_count": {
                "type": "integer",
                "description": "Number of claims with an open status.",
            },
            "total_paid_amount": {
                "type": "number",
                "description": "Sum of paid amounts across all claims, in dollars.",
            },
            "total_reserve": {
                "type": "number",
                "description": "Sum of reserve amounts across all claims, in dollars.",
            },
            "total_incurred": {
                "type": "number",
                "description": "Sum of incurred amounts across all claims, in dollars.",
            },
        },
        "required": [
            "total_claim_count",
            "total_open_count",
            "total_paid_amount",
            "total_reserve",
            "total_incurred",
        ],
    },
}

def return_validated_results(
    file_path: str,
    total_claim_count: int,
    total_open_count: int,
    total_paid_amount: float,
    total_reserve: float,
    total_incurred: float,
) -> dict:
    return {
        "total_claim_count": total_claim_count,
        "total_open_count": total_open_count,
        "total_paid_amount": total_paid_amount,
        "total_reserve": total_reserve,
        "total_incurred": total_incurred,
    }


FUNCTION_DECLARATIONS = [
    extract_claims_declaration,
    focus_pages_declaration,
    validate_totals_declaration,
    return_validated_results_declaration,
]

# Function call name -> implementation. Each takes file_path plus the model's arguments.
FUNCTIONS = {
    "extract_claims": extract_claims,
    "focus_pages": focus_pages,
    "validate_totals": validate_totals,
    "return_validated_results": return_validated_results,
}
