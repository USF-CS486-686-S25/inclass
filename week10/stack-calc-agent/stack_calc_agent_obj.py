from dotenv import load_dotenv
load_dotenv()
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

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

    def mul2(self) -> None:
        """Pop the top two values, multiply them, and push the result back onto the stack."""
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
stack_mul2_tool = FunctionTool.from_defaults(fn = stack.mul2)

llm = OpenAI(model="gpt-4o", temperature=0.0)
agent = ReActAgent.from_tools([stack_push_tool, stack_pop_tool, stack_add2_tool, stack_mul2_tool],
            llm=llm, verbose=True, max_iterations=30)

prompt_v0 = """
You are a stack based calculator.

Use the provided tools to perform the desired computation.

Perform this calucation:

Sum these numbers: 1.1 2.2 3.3 4.4 5.5
"""


prompt = """
You are a stack based calculator.

Use the provided tools to perform the desired computation.

Show your step by step tool call plan, then call the tools to compute the result. Please use all the tools that are need to complete the computation. When using the tools to perform the calculation, for each step think about what needs to be done, perform the Tool Action, reflect on the results, then proceed to the next step.

Perform this calucation:

Sum these numbers: 1.1 2.2 3.3 4.4 5.5
"""

prompt_v1 = """
You are a stack based calculator.

Use the provided tools to perform the desired computation.

Show your step by step tool call plan, then call the tools to compute the result. Please use all the tools that are need to complete the computation. When using the tools to perform the calculation, for each step think about what needs to be done, perform the Tool Action, reflect on the results, then proceed to the next step.

Perform this calucation: 2 * 3 + 4
"""

response = agent.chat(prompt)

print(response)
