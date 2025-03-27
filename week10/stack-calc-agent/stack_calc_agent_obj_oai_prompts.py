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

What is the sum of 1.1, 2.2, 3.3, 4.4, and 5.5?
"""

prompt_v2 = """\
You are a stack-based calculator and you have access to stack tools:

push(value) -> None
pop() -> float
add2() -> None

For example, to add 3 + 4 you can do:
push(3)
push(4)
add2()
result = pop()

Please use the stack tools to answer the following question. Show your plan first, then call the tools as needed, and output the final result.

What is the sum of 1.1, 2.2, 3.3, 4.4, and 5.5?
"""

prompt_v3 = """\
You are a stack-based calculator and you have access to stack tools:

push(value) -> None
pop() -> float
add2() -> None

For example, to add 3 + 4 you can do:
push(3)
push(4)
add2()
result = pop()
The result is {result}.

Please use the stack tools to answer the following question. Show your plan first, then call the tools as needed, and output the final result.

What is the sum of 1.1, 2.2, 3.3, 4.4, and 5.5?
"""

prompt = """\
Task: Calculate the sum of 1.1, 2.2, 3.3, 4.4, and 5.5.
Task Execution Plan:
Push numbers onto the stack:
Use stack_push to add 1.1 to the stack.
Use stack_push to add 2.2 to the stack.
Use stack_push to add 3.3 to the stack.
Use stack_push to add 4.4 to the stack.
Use stack_push to add 5.5 to the stack.
Perform summation:
Use add2 to pop the top two numbers from the stack, add them, and push the result back onto the stack (repeat this step as necessary until all numbers are summed).
Continue this process until the last value remains, which will be the total sum.
Final Result: The final value on the stack will be the sum of all these numbers.
Ensure all operations are conducted in sequence according to stack operations.
"""

prompt = """\
**Task Execution Plan: Calculate the sum of 1.1, 2.2, 3.3, 4.4, and 5.5 using a stack approach.**

1. **Push Numbers onto the Stack:**
    - Push 1.1 onto the stack.
    - Push 2.2 onto the stack.
    - Push 3.3 onto the stack.
    - Push 4.4 onto the stack.
    - Push 5.5 onto the stack.

2. **Pop and Add Numbers:**
    - Pop the top two numbers (5.5 and 4.4) and add them together.
    - Pop the result and the next number (3.3), and add them.
    - Pop the result and the next number (2.2), and add them.
    - Pop the result and the last number (1.1), and add them.

3. **Result:**
    - The final value on the stack is the sum of all the numbers.
"""

prompt = """\
You are a stack-based calculator. Use the provided tools to perform the following
computation. When planning the tools to call be sure to print the contents of the stack
after every tool call using the stack_print_tool tool.
 
What is the sum of 1.1, 2.2, 3.3, 4.4, and 5.5?
"""

response = agent.chat(prompt)

print(response)
