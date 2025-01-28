import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from litellm import completion
import os

import rich

response = completion(
    model = "openrouter/anthropic/claude-3.5-haiku",
    #model = "openrouter/openai/gpt-4o-mini",    
    messages = [{ "content": "Write hello world in C","role": "user"}],
    stream = True
)

#for chunk in response:
#    content = chunk.choices[0].delta.content
#    if content:
#        print(content.strip(), end="")

chunks = []
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        chunks.append(content)

#full_response = "".join(chunks).strip()
full_response = "".join(chunks)
print(full_response)
