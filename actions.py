from dataclasses import dataclass
from typing import Any


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


@dataclass
class ToolReturn:
    """Placeholder for a tool result that can carry PDF chunks back to the model."""

    content: Any = None


async def extract_claims(ctx, page_start=None, page_end=None) -> str:
    """Extract claims from the document. Supports optional page ranges
    for iterative re-extraction of specific sections."""
    raise NotImplementedError


async def focus_pages(ctx, pages: list[int]) -> ToolReturn:
    """Returns high-resolution PDF chunks of specific pages
    for detailed visual inspection."""
    raise NotImplementedError


async def validate_totals(ctx, claims: list[ClaimRecord]) -> str:
    """Validates extracted claims against document totals.
    Checks financial totals AND claim count."""
    raise NotImplementedError


# Gemini function declarations
# https://ai.google.dev/gemini-api/docs/function-calling

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

extract_claims_declaration = {
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

FUNCTION_DECLARATIONS = [
    extract_claims_declaration,
    focus_pages_declaration,
    validate_totals_declaration,
]
