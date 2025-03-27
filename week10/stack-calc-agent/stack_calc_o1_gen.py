from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool, FunctionTool

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value) -> None:
        """Push a value onto the stack."""
        self.stack.append(value)
        print(self.stack)

    def pop(self) -> float:
        """Pop the top value off the stack and return it."""
        if not self.stack:
            raise IndexError("pop from empty stack")
        v = self.stack.pop()
        print(f"v = {v}, {self.stack}")
        return v

    def add2(self) -> None:
        """Pop the top two values, add them, and push the result back onto the stack."""
        if len(self.stack) < 2:
            raise IndexError("not enough elements to perform add2")
        a = self.pop()
        b = self.pop()
        self.push(a + b)
        printf(self.stack)

    def __str__(self):
        return str(self.stack)

stack = Stack()

push_tool = FunctionTool.from_defaults(fn=stack.push)
pop_tool = FunctionTool.from_defaults(fn=stack.pop)
add2_tool = FunctionTool.from_defaults(fn=stack.add2)

llm = OpenAI(model="gpt-4o", temperature=0.0)
agent = OpenAIAgent.from_tools(
    [push_tool, pop_tool, add2_tool],
    llm=llm,
    verbose=True,
    max_iterations=30
)

prompt = """\
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

response = agent.chat(prompt)
print(response)

