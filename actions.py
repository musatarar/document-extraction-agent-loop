from dataclasses import dataclass
from typing import Any

from entities import CLAIM_RECORD_SCHEMA, ClaimRecord

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

FUNCTION_DECLARATIONS = [
    extract_claims_declaration,
    focus_pages_declaration,
    validate_totals_declaration,
]
