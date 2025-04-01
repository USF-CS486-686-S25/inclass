import asyncio
from contextlib import asynccontextmanager

from llama_index.llms.openai import OpenAI
import dotenv
from mcp.client.session import ClientSession

# Load environment variables
dotenv.load_dotenv()

from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context


class StatefulMCPClient(BasicMCPClient):
    """
    Stateful MCP client that maintains a persistent session for call_tool() operations,
    while still creating new sessions for list_tools().
    
    This is useful for stateful MCP servers that need to maintain context between tool calls.
    """
    
    def __init__(self, command_or_url: str, args: list[str] = [], env: dict[str, str] = {}):
        super().__init__(command_or_url, args, env)
        self._session = None
        self._session_cm = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the persistent session if it exists."""
        if self._session is not None:
            try:
                await self._session_cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._session = None
            self._session_cm = None
    
    async def _get_persistent_session(self):
        """Get or create a persistent session."""
        if self._session is None:
            self._session_cm = self._run_session()
            self._session = await self._session_cm.__aenter__()
        return self._session
    
    async def call_tool(self, tool_name: str, arguments: dict):
        """
        Call a tool using a persistent session.
        
        This maintains state between tool calls for stateful MCP servers.
        """
        try:
            session = await self._get_persistent_session()
            return await session.call_tool(tool_name, arguments)
        except Exception as e:
            # If there's an error with the session, try to recover by
            # closing and creating a new session
            await self.close()
            # Retry with a fresh session
            async with self._run_session() as session:
                return await session.call_tool(tool_name, arguments)
    
    # list_tools still uses a new session each time
    async def list_tools(self):
        """
        List available tools, creating a new session each time.
        
        This follows the original behavior of BasicMCPClient for list_tools().
        """
        async with self._run_session() as session:
            return await session.list_tools()
        

# Load LLM
llm = OpenAI(model="gpt-4o")

# Print all available methods for debugging
print(f"FunctionAgent methods: {dir(FunctionAgent)}")

SYSTEM_PROMPT = """\
You are an AI assistant for Tool Calling.

Before you help a user, you need to work with the provided tools.
For playwright tool calls use headless mode.
"""

# Import the StatefulMCPClient class definition from above

async def get_agent(tools: McpToolSpec):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work tools.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    
    #print(f"Agent type: {type(agent)}")
    #print(f"Agent dir: {dir(agent)}")
    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and type(event) == ToolCallResult:
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)

mcp_client = StatefulMCPClient(
    command_or_url="npx", 
    args=["-y", "@executeautomation/playwright-mcp-server"]
)
mcp_tool = McpToolSpec(client=mcp_client)

async def main():    
    # Get the agent
    agent = await get_agent(mcp_tool)
    agent_context = Context(agent)
    
    # Handle a test message
    prompt = "list the first 3 articles on news.ycombinator.com"
    response = await handle_user_message(prompt, agent, agent_context, verbose=True)
    print("Final response:", response)
    
    # Optional: try another prompt with the same session
    #prompt2 = "Now list the top 3 articles"
    #response2 = await handle_user_message(prompt2, agent, agent_context, verbose=True)
    #print("Second response:", response2)

if __name__ == "__main__":
    asyncio.run(main())