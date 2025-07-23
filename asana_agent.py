import asyncio
import os

from superagentx.agent import Agent
from superagentx.agentxpipe import AgentXPipe
from superagentx.engine import Engine
from superagentx.handler.mcp import MCPHandler
from superagentx.llm import LLMClient
from superagentx.prompt import PromptTemplate


async def asana_agent() -> AgentXPipe:
    llm_client = LLMClient(llm_config={"model": "gemini-2.5-flash", "llm_type": "gemini"})
    token = os.getenv("ASANA_ACCESS_TOKEN")

    if not token:
        raise RuntimeError("ASANA_ACCESS_TOKEN is not set in environment.")

    env = os.environ.copy()
    env.update({
        "ASANA_ACCESS_TOKEN": token,
    })

    # This launches the FastMCP Asana tool server via stdio
    handler = MCPHandler(
        command="python",  # or "python3" depending on your environment
        mcp_args=["-m", "asana_mcp.main"],  # run the main.py as a module
        env=env
    )

    prompt = PromptTemplate()

    engine = Engine(
        llm=llm_client,
        handler=handler,
        prompt_template=prompt
    )

    agent = Agent(
        goal="Query tasks, projects, and users in Asana",
        role="Asana Tool Agent",
        llm=llm_client,
        engines=[engine],
        prompt_template=prompt,
        max_retry=1
    )

    return AgentXPipe(agents=[agent])

async def main():
    pipe = await asana_agent()
    user_prompt = input("Enter query: ")
    result = await pipe.flow(user_prompt)
    print("Result:", result[0].result)

if __name__ == "__main__":
    asyncio.run(main())
