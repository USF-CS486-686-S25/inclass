from openai import OpenAI
import os
import logging
import argparse
import json
import colorlog
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

# This script requires additional packages:
# pip install colorlog pygments
#
# Function to pretty print JSON with syntax highlighting
def pretty_json(obj):
    """Format JSON with syntax highlighting for terminal output"""
    if isinstance(obj, (dict, list)):
        json_str = json.dumps(obj, indent=2, sort_keys=True)
        return highlight(json_str, JsonLexer(), TerminalFormatter())
    return str(obj)

# Set up argument parsing
parser = argparse.ArgumentParser(description='OpenAI API tool call example with optional logging')
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
logger = logging.getLogger('openai_toolcall')
logger.setLevel(log_level)
logger.handlers = []  # Remove default handlers
logger.addHandler(handler)
logger.propagate = False

# If no debug or verbose flag, only show WARNING and above
if not (args.debug or args.verbose):
    logger.setLevel(logging.WARNING)

logger.info("Starting OpenAI tool call example")
logger.debug("Setting up OpenAI client")

# Set your API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY environment variable not set")
    
client = OpenAI(api_key=api_key)
logger.debug("OpenAI client initialized")

# Define a simple tool (function)
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
    }
]
logger.debug(f"Defined {len(tools)} tools: \n{pretty_json(tools)}")

# A simple function you could use to handle the tool call
def get_current_weather(location):
    logger.info(f"Getting weather for location: {location}")
    # Normally you'd call an API like OpenWeatherMap here
    logger.debug("Would normally call external weather API here")
    result = {"weather": "sunny", "temperature": "20°C", "location": location}
    logger.debug(f"Weather result: \n{pretty_json(result)}")
    return result

# Start the conversation
logger.info("Starting conversation with OpenAI")
user_query = "What's the weather like in New York?"
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
    
    # See if a tool was called
    tool_calls = response.choices[0].message.tool_calls
    logger.debug(f"Tool calls detected: {bool(tool_calls)}")
    
    if tool_calls:
        logger.info(f"Processing {len(tool_calls)} tool calls")
        for tool_call in tool_calls:
            logger.debug(f"Processing tool call: {tool_call.id}")
            function_name = tool_call.function.name
            logger.info(f"Function called: {function_name}")
            
            # Use json.loads instead of eval for safety
            try:
                logger.debug(f"Parsing arguments: {tool_call.function.arguments}")
                arguments = json.loads(tool_call.function.arguments)
                logger.debug(f"Parsed arguments: \n{pretty_json(arguments)}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse arguments: {e}")
                # Fallback to eval with warning
                logger.warning("Falling back to eval() - NOT recommended for production!")
                arguments = eval(tool_call.function.arguments)
            
            if function_name == "get_current_weather":
                logger.info("Calling get_current_weather function")
                result = get_current_weather(**arguments)
                
                # Send the tool result back to the model
                logger.info("Sending tool result back to OpenAI")
                logger.debug(f"Tool result: \n{pretty_json(result)}")
                
                try:
                    logger.debug("Sending followup request to OpenAI API")
                    followup = client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=[
                            {"role": "user", "content": user_query},
                            response.choices[0].message,
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": str(result),
                            },
                        ]
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
                        print(final_response)
                except Exception as e:
                    logger.error(f"Error in followup request: {e}")
                    raise
            else:
                logger.warning(f"Unknown function name: {function_name}")
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
            print(direct_response)

except Exception as e:
    logger.error(f"Error during OpenAI API call: {str(e)}")
    raise

logger.info("Tool call example completed successfully")
