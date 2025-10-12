# 03_agent_azure.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables from .env file in project root
# First, explicitly clear any existing Azure OpenAI env vars
for key in list(os.environ.keys()):
    if key.startswith('AZURE_OPENAI'):
        del os.environ[key]

# Now load from .env file
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# our tools from Step 2 (DuckDuckGo search + page reader)
from tools import web_search, read_url

# --- LLM (Azure OpenAI) ---
# Uses env vars: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION
# IMPORTANT: 'azure_deployment' is your chat deployment name in Azure
llm = AzureChatOpenAI(
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
    temperature=0.2,
)

tools = [web_search, read_url]

SYSTEM_PROMPT = """You are a Fact-Check Sidekick for Singapore newsroom.
You MUST ground every key claim you output in cited sources with URLs and short quotes.
Workflow:
1) If user gives a paragraph, extract atomic claims (short sentences).
2) For each claim: search the web; open 2-4 promising links; pull short quotes.
3) Compare evidence and return VERDICT per claim: Supported / Contradicted / Unclear.
4) List SOURCES (URLs) and include a brief rationale per source.
Keep a neutral, concise tone. Prefer authoritative/primary sources. Include precise dates."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=6)

if __name__ == "__main__":
    test_input = """Claim: "Singapore will ban petrol cars by 2025."
    Check and provide verdict with sources (2-4)."""
    result = executor.invoke({"input": test_input, "chat_history": []})
    print("\n=== OUTPUT ===\n")
    print(result["output"])