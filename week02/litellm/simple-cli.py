import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from litellm import completion
import os
import sys

response = completion(
    model = "openrouter/anthropic/claude-3.5-haiku",
    messages = [{ "content": sys.argv[1], "role": "user"}],
    stream = True
)

for chunk in response:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
