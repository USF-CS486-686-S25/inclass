from openai import OpenAI
import os
import logging
import argparse
import json
import colorlog
import pytz
from datetime import datetime, timezone as tz
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

# This script requires additional packages:
# pip install colorlog pygments pytz

# Function to pretty print JSON with syntax highlighting
def pretty_json(obj):
    """Format JSON with syntax highlighting for terminal output"""
    if isinstance(obj, (dict, list)):
        json_str = json.dumps(obj, indent=2, sort_keys=True)
        return highlight(json_str, JsonLexer(), TerminalFormatter())
    return str(obj)

# Set up argument parsing
parser = argparse.ArgumentParser(description='OpenAI API tool call example with time and weather functionality')
parser.add_argument('--debug', action='store_true', help='Enable debug logging')
parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
parser.add_argument('--no-color', action='store_true', help='Disable colored output')
args = parser.parse_args()

# Configure logging with colors
log_level = logging.INFO
if args.verbose:
    log_level = logging.INFO
if args.debug:
    log_level = logging.DEBUG

# Define color scheme
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

# Set up colored formatter
handler = colorlog.StreamHandler()
if args.no_color:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
else:
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors=log_colors
    )
handler.setFormatter(formatter)

# Set up logger
logger = logging.getLogger('openai_toolcall_time')
logger.setLevel(log_level)
logger.handlers = []  # Remove default handlers
logger.addHandler(handler)
logger.propagate = False

# If no debug or verbose flag, only show WARNING and above
if not (args.debug or args.verbose):
    logger.setLevel(logging.WARNING)

logger.info("Starting OpenAI tool call example with time functionality")
logger.debug("Setting up OpenAI client")

# Set your API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY environment variable not set")
    
client = OpenAI(api_key=api_key)
logger.debug("OpenAI client initialized")

# Define a function to get current time
def get_current_time(timezone_str=None):
    """Get the current date, time, and timezone
    
    Args:
        timezone_str (str, optional): The timezone to get the time for.
                                  If None, uses local timezone.
                                  Example: 'America/New_York', 'Europe/London', 'Asia/Tokyo'
    """
    logger.info(f"Getting current time for timezone: {timezone_str or 'local'}")
    
    # Get the local time
    now_utc = datetime.now(tz.utc)
    logger.debug(f"Current UTC time: {now_utc}")
    
    # Use the provided timezone or default to system timezone
    if timezone_str:
        try:
            tz_obj = pytz.timezone(timezone_str)
            now = now_utc.astimezone(tz_obj)
            tz_name = timezone_str
            logger.debug(f"Converted to timezone: {timezone_str}")
        except pytz.exceptions.UnknownTimeZoneError:
            # Invalid timezone provided, fallback to UTC
            logger.warning(f"Invalid timezone provided: {timezone_str}, falling back to UTC")
            now = now_utc
            tz_name = f"UTC (invalid timezone provided: {timezone_str})"
    else:
        # Get the local timezone
        now = now_utc.astimezone()
        tz_name = str(now.tzinfo)
        logger.debug(f"Using local timezone: {tz_name}")
    
    # Format the time in a readable way
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    
    result = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "timezone": tz_name,
        "timestamp": formatted_time,
        "utc_offset": now.strftime("%z"),
        "unix_timestamp": int(now.timestamp())
    }
    
    logger.debug(f"Time result: \n{pretty_json(result)}")
    return result

# A simple function you could use to handle the weather tool call
def get_current_weather(location):
    logger.info(f"Getting weather for location: {location}")
    # Normally you'd call an API like OpenWeatherMap here
    logger.debug("Would normally call external weather API here")
    result = {"weather": "sunny", "temperature": "20°C", "location": location}
    logger.debug(f"Weather result: \n{pretty_json(result)}")
    return result

# Define tools (functions)
logger.debug("Defining tools")
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
logger.debug(f"Defined {len(tools)} tools: \n{pretty_json(tools)}")

# Start the conversation with a query that might trigger both tools
logger.info("Starting conversation with OpenAI")
user_query = "What's the weather like in New York? Also, what time is it right now in Tokyo and London?"
logger.debug(f"User query: {user_query}")

try:
    logger.debug("Sending initial request to OpenAI API")
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": user_query}],
        tools=tools,
        tool_choice="auto"
    )
    logger.info("Received response from OpenAI API")
    logger.debug(f"Response: \n{pretty_json(response.model_dump() if hasattr(response, 'model_dump') else response)}")
    
    # Initial response may contain tool calls
    initial_content = response.choices[0].message.content
    if initial_content:
        logger.info(f"Initial content: {initial_content}")
    else:
        logger.info("No initial content, using tools...")
    
    # See if any tools were called
    tool_calls = response.choices[0].message.tool_calls
    logger.debug(f"Tool calls detected: {bool(tool_calls)}")
    
    if tool_calls:
        # Process all tool calls
        logger.info(f"Processing {len(tool_calls)} tool calls")
        
        # Prepare messages for the followup, starting with the original conversation
        followup_messages = [
            {"role": "user", "content": user_query},
            response.choices[0].message  # Include the assistant's response with tool calls
        ]
        
        # Process each tool call
        for tool_call in tool_calls:
            logger.debug(f"Processing tool call: {tool_call.id}")
            function_name = tool_call.function.name
            logger.info(f"Function called: {function_name}")
            
            # Parse arguments safely with json.loads
            try:
                logger.debug(f"Parsing arguments: {tool_call.function.arguments}")
                arguments = json.loads(tool_call.function.arguments)
                logger.debug(f"Parsed arguments: \n{pretty_json(arguments)}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse arguments: {e}")
                # Fallback to eval with warning
                logger.warning("Falling back to eval() - NOT recommended for production!")
                arguments = eval(tool_call.function.arguments)
            
            # Execute the appropriate function
            result = None
            if function_name == "get_current_weather":
                logger.info(f"Calling weather function with location: {arguments.get('location')}")
                result = get_current_weather(arguments.get('location'))
            elif function_name == "get_current_time":
                timezone_str = arguments.get('timezone')
                if timezone_str:
                    logger.info(f"Calling time function with timezone: {timezone_str}")
                    result = get_current_time(timezone_str=timezone_str)
                else:
                    logger.info("Calling time function with local timezone")
                    result = get_current_time()
            else:
                logger.warning(f"Unknown function name: {function_name}")
                continue
            
            # Add this tool result to the messages
            tool_response = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result)  # Properly format as JSON
            }
            followup_messages.append(tool_response)
            
            logger.info(f"Added tool result for {function_name}")
            logger.debug(f"Tool result: \n{pretty_json(result)}")
        
        # Send all the results back to the model
        logger.info("Sending all tool results back to OpenAI")
        try:
            logger.debug("Sending followup request to OpenAI API")
            followup = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=followup_messages
            )
            logger.info("Received followup response from OpenAI API")
            logger.debug(f"Followup response: \n{pretty_json(followup.model_dump() if hasattr(followup, 'model_dump') else followup)}")
            
            final_response = followup.choices[0].message.content
            logger.info("Final response ready")
            logger.debug(f"Final content: {final_response}")
            
            # Print the final response in a highlighted box
            if not args.no_color:
                print("\n" + "=" * 80)
                print("\033[1;32m" + final_response + "\033[0m")
                print("=" * 80 + "\n")
            else:
                print("\nFinal response:")
                print("=" * 50)
                print(final_response)
                print("=" * 50)
        except Exception as e:
            logger.error(f"Error in followup request: {e}")
            raise
    else:
        logger.info("No tool calls detected, using direct response")
        direct_response = response.choices[0].message.content
        logger.debug(f"Direct response: {direct_response}")
        
        # Print the direct response in a highlighted box
        if not args.no_color:
            print("\n" + "=" * 80)
            print("\033[1;32m" + direct_response + "\033[0m")
            print("=" * 80 + "\n")
        else:
            print("\nNo tool calls detected, using direct response:")
            print("=" * 50)
            print(direct_response)
            print("=" * 50)

except Exception as e:
    logger.error(f"Error during OpenAI API call: {str(e)}")
    raise

logger.info("Tool call example completed successfully")