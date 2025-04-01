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

    def print(self):
        """Print the contents of the stack."""
        print(str(self.stack))    

    def __str__(self):
        return str(self.stack)


stack=Stack()

stack_push_tool = FunctionTool.from_defaults(fn = stack.push)
stack_pop_tool = FunctionTool.from_defaults(fn = stack.pop)
stack_add2_tool = FunctionTool.from_defaults(fn = stack.add2)
stack_print_tool = FunctionTool.from_defaults(fn = stack.print)


llm = OpenAI(model="gpt-4o", temperature=0.0)
agent = OpenAIAgent.from_tools(
    [stack_push_tool, stack_pop_tool, stack_add2_tool, stack_print_tool], 
    llm=llm, verbose=True,
    max_iterations=30)

tool_names = "push, pop, add2"
tool_desc = """\
stack_push_tool(value) -> None: Push a value onto the stack.
stack_pop_tool() -> float: Pop the top value off the stack and return it.
stack_add2_tool() -> None: Pop the top two values, add them, and push the result back onto the stack.
"""

prompt_v1 = """\
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

What is the sum of 1.1, 2.2, 3.3, 4.4, 5.5?
"""

prompt = """\
You are a stack-based calculator. Use the provided tools to perform the following
computation. When planning the tools to called be sure to print the contents of the stack
after every tool call using the stack_print_tool tool.
 
What is the sum of 1.1, 2.2, 3.3?
"""

response = agent.chat(prompt_v1)

print(response)
