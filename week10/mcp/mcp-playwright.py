import asyncio

from llama_index.llms.openai import OpenAI
import dotenv

dotenv.load_dotenv()

# Load LLM
llm = OpenAI(model="gpt-4o")

from llama_index.tools.mcp import McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context

SYSTEM_PROMPT = """\
You are an AI assistant for Tool Calling.

Before you help a user, you need to work with the provided tools.
For playwright tool calls use headless mode.
"""


async def get_agent(tools: McpToolSpec):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with tools.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
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


from llama_index.tools.mcp import BasicMCPClient, McpToolSpec


#mcp_client = BasicMCPClient("http://127.0.0.1:3000/sse")

mcp_client = BasicMCPClient(
    command_or_url="npx", 
    args=["-y", "@executeautomation/playwright-mcp-server"]
)
mcp_tool = McpToolSpec(client=mcp_client)

async def main():
    # get the agent
    agent = await get_agent(mcp_tool)
    agent_context = Context(agent)
    
    # optionally handle a test message here
    #prompt = "Retrieve the first 5 articles from http://news.ycombinator.com"
    #prompt = "List the playwright tools"
    prompt = "Summarize news.ycombinator.com"
    
    response = await handle_user_message(prompt, agent, agent_context, verbose=True)
    print("Final response:", response)

if __name__ == "__main__":
    asyncio.run(main())
