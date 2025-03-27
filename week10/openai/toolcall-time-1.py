from openai import OpenAI
import os
import datetime
import json
from tzlocal import get_localzone

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set your API key
# Or just assign the string directly

# Define a function to get current time
def get_current_time():
    """Get the current date, time, and timezone"""
    now = datetime.datetime.now()
    local_tz = get_localzone()
    
    # Format the time in a readable way
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": str(local_tz),
        "timestamp": formatted_time,
        "unix_timestamp": int(now.timestamp())
    }

# A simple function you could use to handle the weather tool call
def get_current_weather(location):
    # Normally you'd call an API like OpenWeatherMap here
    return {"weather": "sunny", "temperature": "20°C", "location": location}

# Define tools (functions)
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date, time, and timezone information",
            "parameters": {
                "type": "object",
                "properties": {},  # No parameters needed
                "required": [],
            },
        },
    }
]

# Start the conversation with a query that might trigger both tools
user_query = "What's the weather like in New York? Also, what time is it right now?"
print(f"User question: {user_query}\n")

response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[{"role": "user", "content": user_query}],
    tools=tools,
    tool_choice="auto"
)

# Initial response may contain tool calls
print(f"Initial response: {response.choices[0].message.content if response.choices[0].message.content else 'No initial content, using tools...'}\n")

# See if any tools were called
tool_calls = response.choices[0].message.tool_calls

if tool_calls:
    # Process all tool calls
    print(f"Processing {len(tool_calls)} tool calls...\n")
    
    # Prepare messages for the followup, starting with the original conversation
    followup_messages = [
        {"role": "user", "content": user_query},
        response.choices[0].message  # Include the assistant's response with tool calls
    ]
    
    # Process each tool call
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        
        # Parse arguments safely with json.loads
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse arguments as JSON, falling back to eval (unsafe for production)")
            arguments = eval(tool_call.function.arguments)
        
        # Execute the appropriate function
        result = None
        if function_name == "get_current_weather":
            print(f"Calling weather function with location: {arguments.get('location')}")
            result = get_current_weather(**arguments)
        elif function_name == "get_current_time":
            print("Calling time function")
            result = get_current_time()
        else:
            print(f"Unknown function: {function_name}")
            continue
        
        # Add this tool result to the messages
        followup_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result)  # Properly format as JSON
        })
        
        print(f"Tool result for {function_name}: {json.dumps(result, indent=2)}\n")
    
    # Send all the results back to the model
    followup = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=followup_messages
    )
    
    # Display the final response
    final_response = followup.choices[0].message.content
    print("Final response:")
    print("=" * 50)
    print(final_response)
    print("=" * 50)
else:
    print("No tool calls detected, using direct response:")
    print("=" * 50)
    print(response.choices[0].message.content)
    print("=" * 50)
