#!/usr/bin/env python3
import sys
from dotenv import load_dotenv
load_dotenv()
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

def fetch_url(url):
    """Fetch content from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Create a function tool from the fetch_url function
fetch_url_tool = FunctionTool.from_defaults(
    fn=fetch_url,
    name="fetch_url",
    description="Fetches content from the specified URL and returns it as text."
)

# Initialize the OpenAI LLM
llm = OpenAI(model="gpt-4o", temperature=0)

# Create an agent with the fetch_url tool
agent = OpenAIAgent.from_tools([fetch_url_tool], llm=llm, verbose=True)

def main():
    """Main function to handle command line arguments and interact with the agent."""
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} \"<your prompt here>\"")
        print("Example: python webtool.py \"Fetch the content from https://example.com and tell me what it's about.\"")
        sys.exit(1)
    
    # Use the command line argument as the prompt
    prompt = ' '.join(sys.argv[1:])
    print(f"Sending prompt to agent: {prompt}")
    
    # Get response from the agent
    response = agent.chat(prompt)
    print(response)

if __name__ == "__main__":
    main()