import asyncio
import logging
import sys

from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

import dotenv

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

dotenv.load_dotenv()



# Load LLM
#llm = OpenAI(model="gpt-4o")
#llm = OpenAI(model="o3-mini")
#llm = Anthropic(model="claude-3-7-sonnet-latest")
llm = Anthropic(model="claude-3-5-sonnet-latest")

from llama_index.tools.mcp import McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context

SYSTEM_PROMPT = """\
You are an AI assistant for Tool Calling.

You can use MCP Run Python to execute generated code to assist in your tasks.
"""


async def get_agent(tools: McpToolSpec):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with tools.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        verbose=True,
    )
    return agent


async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = True,
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
    command_or_url="deno", 
    args=[
        'run',
        '-N',
        '-R=node_modules',
        '-W=node_modules',
        '--node-modules-dir=auto',
        'jsr:@pydantic/mcp-run-python',
        'stdio',
    ],
)

mcp_tool = McpToolSpec(client=mcp_client)

async def main():
    # get the agent
    agent = await get_agent(mcp_tool)
    agent_context = Context(agent)
    
    # optionally handle a test message here
    #prompt = "Retrieve the first 5 articles from http://news.ycombinator.com"
    #prompt = "List the playwright tools"
    #prompt = "Summarize news.ycombinator.com"
    #prompt = "How many days between 2000-01-01 and 2025-03-18?"    
    prompt = "What tools can you use?"
    prompt1 = """Please determine which time slots LS 307 is available during the week, Monday through Friday 8am to 9pm. Use the CSV data below and write and execute python code using the mcp-run-python tool determine the free slots.
    
Select,CRN,Subj,Crse,Sec,Cmp,Cred,Title,Days,Time,Cap,Act,Rem,WL Cap,WL Act,WL Rem,XL Cap,XL Act,XL Rem,Instructor,Date (MM/DD),Location,Attribute
C,40427,CS,107,01,M,4.000,Computing Mobile Apps & Web,MW,04:45 pm-06:25 pm,25,25,0,0,0,0,0,0,0,Andrew Rothman (P),08/19-12/11,HR 148,"Core B1 Math or Quant Sci and Education: Liberal Studies and In-Person Modality and Tuition (Sciences)"
SR,40428,CS,107,02,M,4.000,Computing Mobile Apps & Web,MW,06:30 pm-08:15 pm,25,10,15,0,0,0,0,0,0,Andrew Rothman (P),08/19-12/11,HR 148,"Core B1 Math or Quant Sci and Education: Liberal Studies and In-Person Modality and Tuition (Sciences)"
SR,40430,CS,110,01,M,4.000,Intro to Computer Science,MW,11:15 am-01:00 pm,20,3,17,0,0,0,0,0,0,Nancy R Stevens (P),08/19-12/11,HR 148,"Core B1 Math or Quant Sci and In-Person Modality and Tuition (Sciences)"
SR,40431,CS,110,02,M,4.000,Intro to Computer Science,TR,09:55 am-11:40 am,20,0,20,0,0,0,0,0,0,Kelsey Urgo (P),08/19-12/11,LS 307,"Core B1 Math or Quant Sci and In-Person Modality and Tuition (Sciences)"
SR,40432,CS,110,03,M,4.000,Intro to Computer Science,TR,02:40 pm-04:25 pm,20,3,17,0,0,0,0,0,0,Julia Marie Nolfo (P),08/19-12/11,LS G12,"Core B1 Math or Quant Sci and In-Person Modality and Tuition (Sciences)"
SR,40433,CS,110,04,M,4.000,Intro to Computer Science,TR,04:30 pm-06:20 pm,20,3,17,0,0,0,0,0,0,Julia Marie Nolfo (P),08/19-12/11,LS G12,"Core B1 Math or Quant Sci and In-Person Modality and Tuition (Sciences)"
SR,40434,CS,111,01,M,4.000,Foundations of Program Design,MW,12:10 pm-01:55 pm,20,6,14,0,0,0,0,0,0,Edward Rees (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
SR,40435,CS,111,02,M,4.000,Foundations of Program Design,MW,02:15 pm-04:00 pm,20,5,15,0,0,0,0,0,0,Edward Rees (P),08/19-12/11,LS G12,"In-Person Modality and Tuition (Sciences)"
C,40436,CS,112,01,M,4.000,Intro to Computer Science II,TR,09:55 am-11:40 am,20,20,0,0,0,0,0,0,0,Alark P Joshi (P),08/19-12/11,LS G12,"In-Person Modality and Tuition (Sciences)"
C,40437,CS,112,02,M,4.000,Intro to Computer Science II,TR,12:45 pm-02:30 pm,20,20,0,0,0,0,0,0,0,Alark P Joshi (P),08/19-12/11,LS G12,"In-Person Modality and Tuition (Sciences)"
SR,42067,CS,186,01,M,2.000,SpTp: Comm Engaged CS,F,11:00 am-12:45 pm,20,1,19,0,0,0,0,0,0,Mehmet Emre (P),08/19-12/11,HR 148,"Tuition (Sciences)"
SR,40438,CS,221,01,M,4.000,C and Systems Programming,MW,09:20 am-11:05 am,20,19,1,0,0,0,0,0,0,Paul Haskell (P),08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
SR,40439,CS,221,02,M,4.000,C and Systems Programming,MW,01:10 pm-02:55 pm,20,19,1,0,0,0,0,0,0,Paul Haskell (P),08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
SR,40441,CS,245,01,M,4.000,Data Struct & Algorithms,MWF,09:15 am-10:20 am,20,3,17,0,0,0,0,0,0,Eunjin Jung (P),08/19-12/11,ED 306,"In-Person Modality and Tuition (Sciences)"
SR,41734,CS,245,02,M,4.000,Data Struct & Algorithms,MWF,10:30 am-11:35 am,20,5,15,0,0,0,0,0,0,Eunjin Jung (P),08/19-12/11,ED 103,"In-Person Modality and Tuition (Sciences)"
C,40442,CS,245,03,M,4.000,Data Struct & Algorithms,MWF,11:45 am-12:50 pm,20,20,0,5,3,2,0,0,0,David-Guy Brizan (P),08/19-12/11,ED 103,"In-Person Modality and Tuition (Sciences)"
SR,41871,CS,245L,01,M,0.000,Data Struct & Algorithms Lab,M,01:00 pm-02:05 pm,20,2,18,0,0,0,0,0,0,Eunjin Jung (P),08/19-12/11,ED 103,"In-Person Modality and Tuition (Liberal Arts)"
C,40443,CS,256,01,M,2.000,Career Prep,R,06:30 pm-08:15 pm,20,17,3,0,0,0,20,24,-4,Jon Sebastian Rahoi (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
SR,40444,CS,272,01,M,4.000,Software Development,TR,08:00 am-09:45 am,20,17,3,20,1,19,0,0,0,Philip H Peterson (P),08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
C,40445,CS,272,02,M,4.000,Software Development,TR,02:40 pm-04:25 pm,20,20,0,20,2,18,0,0,0,Philip H Peterson (P),08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
C,40469,CS,272L,01,M,0.000,Software Development Lab,W,01:00 pm-02:30 pm,20,20,0,20,3,17,0,0,0,Philip H Peterson (P),08/19-12/11,ED 104,"In-Person Modality and Tuition (Sciences)"
SR,40470,CS,272L,02,M,0.000,Software Development Lab,W,02:55 pm-04:25 pm,20,17,3,20,1,19,0,0,0,Philip H Peterson (P),08/19-12/11,ED 104,"In-Person Modality and Tuition (Sciences)"
C,40446,CS,315,01,M,4.000,Computer Architecture,TR,08:00 am-09:45 am,20,20,0,20,1,19,0,0,0,Gregory D Benson (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
C,40447,CS,315,02,M,4.000,Computer Architecture,TR,02:40 pm-04:25 pm,20,20,0,20,5,15,0,0,0,Gregory D Benson (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
C,40471,CS,315L,01,M,0.000,Laboratory,W,04:45 pm-06:15 pm,20,20,0,20,5,15,0,0,0,Gregory D Benson (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
C,40472,CS,315L,02,M,0.000,Laboratory,W,06:25 pm-07:55 pm,20,20,0,20,0,20,0,0,0,Gregory D Benson (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
C,41731,CS,326,01,M,4.000,Operating Systems,MW,09:55 am-11:40 am,20,22,-2,20,11,9,0,0,0,Matthew Malensek (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
C,41732,CS,326L,01,M,0.000,Laboratory,M,12:30 pm-02:00 pm,20,22,-2,20,11,9,0,0,0,Matthew Malensek (P),08/19-12/11,ED 006,"In-Person Modality and Tuition (Sciences)"
C,40448,CS,345,01,M,4.000,Prog Language Paradigms,MWF,09:15 am-10:20 am,20,21,-1,20,3,17,0,0,0,Kristin Alise Jones (P),08/19-12/11,ED 103,"In-Person Modality and Tuition (Sciences)"
C,40449,CS,345,02,M,4.000,Prog Language Paradigms,TR,02:40 pm-04:25 pm,20,20,0,0,0,0,0,0,0,Mehmet Emre (P),08/19-12/11,ED 006,"In-Person Modality and Tuition (Sciences)"
C,40450,CS,362,01,M,4.000,Foundations of AI,MWF,10:30 am-11:35 am,10,10,0,10,10,0,20,18,2,David-Guy Brizan (P),08/19-12/11,MH 126,"In-Person Modality and Tuition (Sciences)"
SR,40451,CS,386,01,M,4.000,Sp Topics in Computer Sci,MW,04:45 pm-06:25 pm,20,6,14,0,0,0,0,0,0,Michael Kremer (P),08/19-12/11,LM 244A,"In-Person Modality and Tuition (Sciences)"
SR,41787,CS,386,03,M,2.000,SpTp: Game Dev with Unity,R,04:35 pm-06:20 pm,25,12,13,0,0,0,0,0,0,TBA,08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
C,41733,CS,463,01,M,4.000,Foundations of ML,TR,12:45 pm-02:30 pm,20,20,0,20,3,17,0,0,0,Kelsey Urgo (P),08/19-12/11,LS 307,"Tuition (Sciences)"
SR,42196,CS,486,01,M,4.000,SpTp: Natural Language Process,MWF,11:45 am-12:50 pm,10,8,2,0,0,0,30,28,2,Kristin Alise Jones (P),08/19-12/11,LM 350,"In-Person Modality and Tuition (Sciences)"
SR,42197,CS,486,02,M,4.000,SpTp: Program Synthesis,TR,04:35 pm-06:20 pm,10,5,5,0,0,0,30,20,10,Mehmet Emre (P),08/19-12/11,LS 307,"Tuition (Sciences)"
C,41785,CS,486,06,M,4.000,SpTp: Ethical Trustworthy AI,TR,12:45 pm-02:30 pm,10,10,0,0,0,0,20,11,9,TBA,08/19-12/11,LM 350,"In-Person Modality and Tuition (Sciences)"
C,40454,CS,490,01,M,4.000,Senior Team Project,MW,04:45 pm-06:25 pm,24,24,0,24,5,19,0,0,0,Paul Haskell (P),08/19-12/11,CO 106,"In-Person Modality and Tuition (Sciences)"
SR,40455,CS,490,02,M,4.000,Senior Team Project,F,09:15 am-12:55 pm,20,12,8,0,0,0,0,0,0,Jagadeesan Krishnamurthy (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
SR,40456,CS,514,01,M,6.000,Object-Oriented Programming,MW,02:05 pm-04:40 pm,25,1,24,0,0,0,0,0,0,David W Wolber (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
SR,40457,CS,562,01,M,4.000,Foundations of AI,MWF,10:30 am-11:35 am,10,8,2,10,0,10,20,18,2,David-Guy Brizan (P),08/19-12/11,MH 126,"In-Person Modality and Tuition (Sciences)"
SR,40458,CS,601,01,M,4.000,Principles SW Development,TR,09:55 am-11:40 am,25,12,13,0,0,0,0,0,0,Olga Karpenko (P),08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
SR,40459,CS,601,02,M,4.000,Principles SW Development,TR,12:45 pm-02:30 pm,25,6,19,0,0,0,0,0,0,Olga Karpenko (P),08/19-12/11,HR 148,"In-Person Modality and Tuition (Sciences)"
SR,42098,CS,601L,01,ODP,0.000,Principles SW Development Lab,F,02:00 pm-03:30 pm,25,18,7,0,0,0,0,0,0,Olga Karpenko (P),08/19-12/11,ONL ONL,"Tuition (Sciences)"
SR,42099,CS,601L,02,ODP,0.000,Principles SW Development Lab,F,04:00 pm-05:30 pm,25,0,25,0,0,0,0,0,0,Olga Karpenko (P),08/19-12/11,ONL ONL,"Tuition (Sciences)"
SR,40460,CS,603,01,M,4.000,Algorithms,W,09:55 am-11:40 am,25,8,17,0,0,0,0,0,0,Ellen Veomett (P),08/19-12/11,LS G12,"In-Person Modality and Tuition (Sciences)"
,,,,,,,,,F 09:55 am-11:40 am,,,,,,,,,,,Ellen Veomett (P),08/19-12/11,ONL ONL,"In-Person Modality and Tuition (Sciences)"
SR,40461,CS,603,02,M,4.000,Algorithms,W,12:10 pm-01:55 pm,25,16,9,0,0,0,0,0,0,Ellen Veomett (P),08/19-12/11,LS G12,"In-Person Modality and Tuition (Sciences)"
,,,,,,,,,F 12:10 pm-01:55 pm,,,,,,,,,,,Ellen Veomett (P),08/19-12/11,ONL ONL,"In-Person Modality and Tuition (Sciences)"
C,40463,CS,686,02,M,4.000,SpTp: Natural Language Process,MWF,11:45 am-12:50 pm,20,20,0,0,0,0,30,28,2,Kristin Alise Jones (P),08/19-12/11,LM 350,"In-Person Modality and Tuition (Sciences)"
C,42158,CS,686,03,M,2.000,SpTp: Career Prep,R,06:30 pm-08:15 pm,15,7,8,0,0,0,20,24,-4,Jon Sebastian Rahoi (P),08/19-12/11,LS 307,"Tuition (Sciences)"
SR,40465,CS,686,04,M,4.000,SpTp: Program Synthesis,TR,04:35 pm-06:20 pm,20,15,5,0,0,0,30,20,10,Mehmet Emre (P),08/19-12/11,LS 307,"In-Person Modality and Tuition (Sciences)"
SR,40466,CS,686,05,M,4.000,SpTp: Cloud Computing,MW,02:15 pm-04:00 pm,20,18,2,0,0,0,0,0,0,Mario Junior Lim Kam (P),08/19-12/11,ED 103,"In-Person Modality and Tuition (Sciences)"
SR,41786,CS,686,06,M,4.000,SpTp:Ethical Trustworthy AI,TR,12:45 pm-02:30 pm,10,1,9,0,0,0,20,11,9,TBA,08/19-12/11,LM 350,"In-Person Modality and Tuition (Sciences)"
SR,40467,CS,690,01,M,4.000,Master's Project,TR,02:40 pm-04:25 pm,20,15,5,0,0,0,0,0,0,Olga Karpenko (P),08/19-12/11,ED 103,"In-Person Modality and Tuition (Sciences)"
C,40468,CS,690,02,M,4.000,Master's Project,MW,04:45 pm-06:25 pm,20,21,-1,0,0,0,0,0,0,Mario Junior Lim Kam (P),08/19-12/11,LS G12,"In-Person Modality and Tuition (Sciences)"
SR,42157,CS,695,01,M,2.000,Practicum Study,,TBA,20,0,20,0,0,0,0,0,0,Matthew Malensek (P),08/19-12/11,TBA,"Tuition (Sciences)"
"""
    response = await handle_user_message(prompt, agent, agent_context, verbose=True)
    print("Final response:", response)

if __name__ == "__main__":
    asyncio.run(main())
