from dotenv import load_dotenv
load_dotenv()
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        """Push a value onto the stack."""
        self.stack.append(value)

    def pop(self):
        """Pop the top value off the stack and return it."""
        if not self.stack:
            raise IndexError("pop from empty stack")
        return self.stack.pop()

    def add2(self):
        """Pop the top two values, add them, and push the result back onto the stack."""
        if len(self.stack) < 2:
            raise IndexError("not enough elements to perform add2")
        a = self.pop()
        b = self.pop()
        self.push(a + b)

    def __str__(self):
        return str(self.stack)


stack=Stack()

def stack_push(value: float) -> str:
    """Push a value onto the stack."""
    stack.push(value)
    print(stack)
    return "{value} pushed."

stack_push_tool = FunctionTool.from_defaults(fn=stack_push)


def stack_pop() -> float:
    """Pop a value off the stack and return the value."""
    print(stack)
    return stack.pop()

stack_pop_tool = FunctionTool.from_defaults(fn=stack_pop)

def stack_add2() -> str:
    """Pop the top to values off the stack, add them, and put sum on the stack."""
    stack.add2()
    print(stack)
    return "Top two values added."

stack_add2_tool = FunctionTool.from_defaults(fn=stack_add2)


llm = OpenAI(model="gpt-4o", temperature=0.0)
agent = ReActAgent.from_tools([stack_push_tool, stack_pop_tool, stack_add2_tool],
            llm=llm, verbose=True, max_iterations=30)

prompt = """
You are a stack based calculator.

Use the provided tools to perform the desired computation.

Show your step by step tool call plan, then call the tools to compute the result. Please use all the tools that are need to complete the computation.

Perform this calucation:

Sum these numbers: 1.1 2.2 3.3 4.4 5.5
"""

response = agent.chat(prompt)

print(response)
