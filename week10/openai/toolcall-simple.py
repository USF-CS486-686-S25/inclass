from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set your API key
# Or just assign the string directly

# Define a simple tool (function)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

# A simple function you could use to handle the tool call
def get_current_weather(location):
    # Normally you'd call an API like OpenWeatherMap here
    return {"weather": "sunny", "temperature": "20°C", "location": location}

# Start the conversation
response = client.chat.completions.create(model="gpt-4-1106-preview",
messages=[{"role": "user", "content": "What's the weather like in New York?"}],
tools=tools,
tool_choice="auto")

# See if a tool was called
tool_calls = response.choices[0].message.tool_calls

# Pretty print the tool_calls object as JSON
if tool_calls:
    # Convert tool_calls to a JSON-serializable structure
    tool_calls_json = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id": tool_call.id,
            "type": tool_call.type,
            "function": {
                "name": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            }
        }
        tool_calls_json.append(tool_call_dict)
    
    # Print the formatted JSON
    print("Tool Calls (JSON format):")
    print(json.dumps(tool_calls_json, indent=4))
    print("\n")

if tool_calls:
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)  # Safer than eval
        if function_name == "get_current_weather":
            result = get_current_weather(**arguments)

            # Send the tool result back to the model
            followup = client.chat.completions.create(model="gpt-4-1106-preview",
            messages=[
                {"role": "user", "content": "What's the weather like in New York?"},
                response.choices[0].message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(result),
                },
            ])

            print(followup.choices[0].message.content)
else:
    print(response.choices[0].message.content)
