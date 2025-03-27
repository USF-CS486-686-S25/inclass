from dotenv import load_dotenv
load_dotenv()
#from llama_index.core.agent import ReActAgent
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool


import logging
import sys

#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
#logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value) -> None:
        """Push a value onto the stack."""
        self.stack.append(value)

    def pop(self) -> float:
        """Pop the top value off the stack and return it."""
        if not self.stack:
            raise IndexError("pop from empty stack")
        return self.stack.pop()

    def add2(self) -> None:
        """Pop the top two values, add them, and push the result back onto the stack."""
        if len(self.stack) < 2:
            raise IndexError("not enough elements to perform add2")
        a = self.pop()
        b = self.pop()
        self.push(a + b)

    def __str__(self):
        return str(self.stack)


stack=Stack()

stack_push_tool = FunctionTool.from_defaults(fn = stack.push)
stack_pop_tool = FunctionTool.from_defaults(fn = stack.pop)
stack_add2_tool = FunctionTool.from_defaults(fn = stack.add2)

# def stack_push(value: float) -> str:
    # """Push a value onto the stack."""
    # stack.push(value)
    # print(stack)
    # return "{value} pushed."
# 
# stack_push_tool = FunctionTool.from_defaults(fn=stack_push)
# 
# 
# def stack_pop() -> float:
    # """Pop a value off the stack and return the value."""
    # print(stack)
    # return stack.pop()
# 
# stack_pop_tool = FunctionTool.from_defaults(fn=stack_pop)
# 
# def stack_add2() -> str:
    # """Pop the top to values off the stack, add them, and put sum on the stack."""
    # stack.add2()
    # print(stack)
    # return "Top two values added."
# 
# stack_add2_tool = FunctionTool.from_defaults(fn=stack_add2)


llm = OpenAI(model="gpt-4o", temperature=0.0)
#agent = ReActAgent.from_tools([stack_push_tool, stack_pop_tool, stack_add2_tool],
#            llm=llm, verbose=True, max_iterations=30)
agent = OpenAIAgent.from_tools(
    [stack_push_tool, stack_pop_tool, stack_add2_tool], llm=llm, verbose=True,
    max_iterations=30)

tool_names = "stack_push_tool, stack_pop_tool, stack_add2_tool"
tool_desc = """\
stack_push_tool(value) -> None: Push a value onto the stack.
stack_pop_tool() -> float: Pop the top value off the stack and return it.
stack_add2_tool() -> None: Pop the top two values, add them, and push the result back onto the stack.
"""
user_prompt = """
Perform this calucation:

Sum these numbers: 1.1 2.2 3.3 4.4 5.5
"""

prompt1 = f"""\
You are designed to help with a variety of tasks, from answering questions 
to providing summaries to other types of analyses.

## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

```
Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

```
Thought: I can answer without using any more tools.
Answer: [your answer here]
```

```
Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.
```

## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

{user_prompt}
"""

prompt = """\
You are a stack-based calculator and you have access to stack tools:

stack_push_tool(value) -> None
stack_pop_tool() -> float
stack_add2_tool() -> None

For example to add 3 + 4 you can do:
stack_push_tool(3)
stack_push_tool(4)
stack_add2_tool()
result = stack_pop()

Please use the stack tools to
answer the following question. Show your plan first, then call the tools as needed.

What is the sum of 1.1, 2.2, 3.3, 4.4, and 5.5?
"""

response = agent.chat(prompt)

print(response)
