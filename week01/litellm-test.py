import os
from litellm import completion

response = completion(
            model="openrouter/anthropic/claude-3.5-sonnet",
            messages=[{"content": "What is 1 + 2?", "role": "user"}]
        )

print(response.choices[0].message.content)
