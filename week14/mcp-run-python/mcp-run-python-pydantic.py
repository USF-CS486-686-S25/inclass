from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

#import logfire

#logfire.configure()
#logfire.instrument_mcp()
#logfire.instrument_pydantic_ai()

server = MCPServerStdio('deno',
    args=[
        'run',
        '-N',
        '-R=node_modules',
        '-W=node_modules',
        '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio',
    ])
agent = Agent('claude-3-5-haiku-latest', mcp_servers=[server])


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    #> There are 9,208 days between January 1, 2000, and March 18, 2025.


    #async with agent.iter('How many days between 2000-01-01 and 2025-03-18?') as agent_run:
    #    async for node in agent_run:
    #        print(node)
    #print(agent_run.result.output)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
