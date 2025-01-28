import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from litellm import completion
import os

import rich

response = completion(
  model="openrouter/anthropic/claude-3.5-sonnet",
  messages = [{ "content": "Write hello world in C. Just provide the C code without explanation.",
                "role": "user"}],
)

print("== Respose Object ===")
rich.pretty.pprint(response)

print("=== Response ===")
print(response.choices[0].message.content)
