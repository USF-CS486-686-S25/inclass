from openai import OpenAI
import os
import json
import pytz
from datetime import datetime, timezone as tz

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set your API key
# Or just assign the string directly

# Define a function to get current time
def get_current_time(timezone_str=None):
    """Get the current date, time, and timezone
    
    Args:
        timezone_str (str, optional): The timezone to get the time for.
                                  If None, uses local timezone.
                                  Example: 'America/New_York', 'Europe/London', 'Asia/Tokyo'
    """
    # Get the local time
    now_utc = datetime.now(tz.utc)
    
    # Use the provided timezone or default to system timezone
    if timezone_str:
        try:
            tz_obj = pytz.timezone(timezone_str)
            now = now_utc.astimezone(tz_obj)
            tz_name = timezone_str
        except pytz.exceptions.UnknownTimeZoneError:
            # Invalid timezone provided, fallback to UTC
            now = now_utc
            tz_name = f"UTC (invalid timezone provided: {timezone_str})"
    else:
        # Get the local timezone
        now = now_utc.astimezone()
        tz_name = str(now.tzinfo)
    
    # Format the time in a readable way
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": tz_name,
        "timestamp": formatted_time,
        "utc_offset": now.strftime("%z"),
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
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Optional timezone in format 'Area/Location', e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo'. If not provided, the local system timezone is used.",
                    }
                },
                "required": [],  # timezone is optional
            },
        },
    }
]

# Start the conversation with a query that might trigger both tools
user_query = "What's the weather like in New York? Also, what time is it right now in Tokyo and London?"
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
            timezone_str = arguments.get('timezone')
            if timezone_str:
                print(f"Calling time function with timezone: {timezone_str}")
                result = get_current_time(timezone_str=timezone_str)
            else:
                print("Calling time function with local timezone")
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
