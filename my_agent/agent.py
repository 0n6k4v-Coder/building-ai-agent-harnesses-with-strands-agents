import os
from dotenv import load_dotenv
from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models.openai import OpenAIModel

# Load the .env file from one level up (Root folder)
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Determine the active provider from environment variables (defaults to 'thaillm')
model = OpenAIModel(
    client_args={
        "api_key": os.getenv("NVIDIA_API_KEY"),
        "base_url": os.getenv("NVIDIA_BASE_URL"),
        "default_headers": {"User-Agent": "Mozilla/5.0"}
    },
    model_id=os.getenv("NVIDIA_MODEL_ID"),
)

# Define a custom tool as a Python function using the @tool decorator
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0

    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())

# Create an agent with tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent(
    model=model,
    tools=[calculator, current_time, letter_counter]
)

# Ask the agent a question that uses the available tools
message = """
I have 4 requests:

1. What is the time right now?
2. Calculate 3111696 / 74088
3. Tell me how many letter R's are in the word "strawberry" 🍓
"""
agent(message)