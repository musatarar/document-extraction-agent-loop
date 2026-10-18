import json
from google import genai
from models import CLAIM_RECORD_SCHEMA
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field

from utils.pdf import pdf_to_base64

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client()


def interact(
    input: str, 
    response_format: BaseModel = None,
    thinking_level: str = "low", 
    tools: list[dict] | None = None
) -> str:
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=input,
        **({"tools": tools} if tools else {}),
        response_format=response_format,
        generation_config={
            "thinking_level": thinking_level,
            "thinking_summaries": "auto"
        }
    )
    return interaction

def parse_tool_call(interaction) -> tuple:
    final_step = interaction.steps[-1]
    if final_step.type == "function_call":
        return final_step.name, final_step.arguments
    return None


# Document parsing calls

class DocumentTotals(BaseModel):
    total_claims: int | None = Field(description="The total number of claims in the document", default=None)
    total_paid: float | None = Field(description="The total amount paid for the claims", default=None)
    total_outstanding: float | None = Field(description="The total amount outstanding for the claims", default=None)
    total_reserve: float | None = Field(description="The total amount reserved for the claims", default=None)
    total_incurred: float | None = Field(description="The total amount incurred for the claims", default=None)

def get_document_totals(file_path: str, pages = None) -> str:
    interaction = interact([
        {
            "type": "document",
            "data": pdf_to_base64(file_path, pages),
            "mime_type": "application/pdf"
        },
        {"type": "text", "text": "Return the total number of claims, the total amount paid, the total amount outstanding, the total amount reserved, and the total amount incurred. Leave any fields that you are not sure about as None."}
    ], response_format=DocumentTotals.model_json_schema())

    return DocumentTotals.model_validate_json(interaction.output_text)

def inspect_pages(file_path: str, pages: list[int], prompt) -> str:
    interaction = interact([
        {
            "type": "document",
            "data": pdf_to_base64(file_path, pages),
            "mime_type": "application/pdf"
        },
        {"type": "text", "text": prompt}
    ])
    return interaction.output_text

CLAIMS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"claims": {"type": "array", "items": CLAIM_RECORD_SCHEMA}},
    "required": ["claims"],
}

def get_document_claims(file_path: str, pages: list[int] | None = None, prompt: str = "Return every claim in the document, one record per claim. Copy dollar amounts exactly as shown, as floats. If a field is not shown, use an empty string for text and 0 for amounts.") -> list[dict]:
    interaction = interact([
        {
            "type": "document",
            "data": pdf_to_base64(file_path, pages),
            "mime_type": "application/pdf"
        },
        {"type": "text", "text": prompt}
    ], response_format=CLAIMS_RESPONSE_SCHEMA)
    return json.loads(interaction.output_text)["claims"]
