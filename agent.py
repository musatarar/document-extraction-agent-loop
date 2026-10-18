from google import genai
from actions import FUNCTION_DECLARATIONS
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client()


def interact(input: str, thinking_level: str = "low", tools: list[dict] = FUNCTION_DECLARATIONS) -> str:
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=input,
        tools=tools,
        generation_config={
            "thinking_level": thinking_level,
            "thinking_summaries": "auto"
        }
    )
    return interaction

def parse_tool_call(interaction) -> dict:
    for step in interaction.steps:
        if step.type == "function_call":
            print(f"Function to call: {step.name}")
            print(f"Arguments: {step.arguments}")
    return None


