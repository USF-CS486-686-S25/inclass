import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from litellm import completion
import os
import rich

# Set up the messages array
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "And what's the capital of Italy?"}
]
# Make the API call
try:
    response = completion(
        model="openrouter/anthropic/claude-3.5-haiku",
        messages=messages
    )

    print("== Respose Object ===")
    rich.pretty.pprint(response)

    print("=== Response ===")
    print(response.choices[0].message.content)
        

except Exception as e:
    print(f"An error occurred: {e}")
    
