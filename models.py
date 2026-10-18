from dataclasses import dataclass

from dataclasses import dataclass

@dataclass
class FinancialBucket:
    paid: float
    reserve: float
    incurred: float

@dataclass
class Financials:
    indemnity: FinancialBucket
    medical: FinancialBucket
    expense: FinancialBucket


@dataclass
class ClaimRecord:
    """A single claim extracted from a loss run."""

    claim_number: str
    coverage: str
    date_of_loss: str
    date_reported: str
    date_closed: str | None
    status: str
    claimant: str
    cause: str
    description: str
    location: str
    financials: Financials
    recovery: float
    total_paid: float
    total_reserve: float
    total_incurred: float
    paid_loss: float
    paid_expense: float
    reserve_loss: float
    reserve_expense: float
    net_incurred: float

_FINANCIAL_BUCKET_SCHEMA = {
    "type": "object",
    "properties": {
        "paid": {"type": "number"},
        "reserve": {"type": "number"},
        "incurred": {"type": "number"},
    },
    "required": ["paid", "reserve", "incurred"],
}

CLAIM_RECORD_SCHEMA = {
    "type": "object",
    "properties": {
        "claim_number": {"type": "string"},
        "coverage": {"type": "string", "description": "Line of coverage, e.g. WC."},
        "date_of_loss": {"type": "string", "description": "YYYY-MM-DD"},
        "date_reported": {"type": "string", "description": "YYYY-MM-DD"},
        "date_closed": {"type": "string", "nullable": True, "description": "YYYY-MM-DD; null if open."},
        "status": {"type": "string", "description": "e.g. Open, Closed."},
        "claimant": {"type": "string"},
        "cause": {"type": "string"},
        "description": {"type": "string"},
        "location": {"type": "string"},
        "financials": {
            "type": "object",
            "properties": {
                "indemnity": _FINANCIAL_BUCKET_SCHEMA,
                "medical": _FINANCIAL_BUCKET_SCHEMA,
                "expense": _FINANCIAL_BUCKET_SCHEMA,
            },
            "required": ["indemnity", "medical", "expense"],
        },
        "recovery": {"type": "number"},
        "total_paid": {"type": "number"},
        "total_reserve": {"type": "number"},
        "total_incurred": {"type": "number"},
        "paid_loss": {"type": "number"},
        "paid_expense": {"type": "number"},
        "reserve_loss": {"type": "number"},
        "reserve_expense": {"type": "number"},
        "net_incurred": {"type": "number"},
    },
    "required": [
        "claim_number", "coverage", "date_of_loss", "date_reported", "date_closed",
        "status", "claimant", "cause", "description", "location", "financials",
        "recovery", "total_paid", "total_reserve", "total_incurred", "paid_loss",
        "paid_expense", "reserve_loss", "reserve_expense", "net_incurred",
    ],
}

# Gemini function declarations
# https://ai.google.dev/gemini-api/docs/function-calling


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
        },
        "required": ["pages"],
    },
}

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

FUNCTION_DECLARATIONS = [
    extract_claims_declaration,
    focus_pages_declaration,
    validate_totals_declaration,
    return_validated_results_declaration,
]
