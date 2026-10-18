import os
import sys

# agent.py builds a genai.Client at import time, which needs a key to be set
os.environ.setdefault("GEMINI_API_KEY", "test")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
