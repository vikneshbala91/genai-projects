#!/usr/bin/env python3
"""Flask app for Fact-Check Sidekick chatbot"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler

# Add the src directory to Python path so imports work from any directory
src_dir = Path(__file__).parent.resolve()
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file in project root
# First, explicitly clear any existing Azure OpenAI env vars
for key in list(os.environ.keys()):
    if key.startswith('AZURE_OPENAI'):
        del os.environ[key]

# Now load from .env file
project_root = src_dir.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

logger.info(f"Loading .env from: {env_path}")
logger.info(f"Flask templates will be loaded from: {src_dir / 'templates'}")

# Import tools (now that src_dir is in sys.path)
from tools import web_search, read_url


# Custom callback handler to log tool invocations
class ToolLoggingCallback(BaseCallbackHandler):
    """Callback handler to log tool invocations and outputs"""

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Log when a tool starts"""
        tool_name = serialized.get("name", "Unknown Tool")
        logger.info(f"\n{'='*60}")
        logger.info(f"🔧 TOOL INVOKED: {tool_name}")
        logger.info(f"📥 INPUT: {input_str}")
        logger.info(f"{'='*60}")
        # BREAKPOINT HERE: Set breakpoint on this line to catch tool invocations

    def on_tool_end(self, output, **kwargs):
        """Log when a tool completes"""
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ TOOL OUTPUT:")
        logger.info(f"{output[:500]}..." if len(str(output)) > 500 else output)
        logger.info(f"{'='*60}\n")
        # BREAKPOINT HERE: Set breakpoint on this line to see tool outputs

    def on_tool_error(self, error, **kwargs):
        """Log tool errors"""
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ TOOL ERROR: {error}")
        logger.error(f"{'='*60}\n")
        # BREAKPOINT HERE: Set breakpoint on this line to catch tool errors

    def on_agent_action(self, action, **kwargs):
        """Log agent actions"""
        logger.info(f"\n🤖 AGENT ACTION: {action.tool}")
        logger.info(f"📋 Action Input: {action.tool_input}")
        # BREAKPOINT HERE: Set breakpoint on this line to see agent decisions


# Initialize Flask with explicit template and static folder paths
app = Flask(
    __name__,
    template_folder=str(src_dir / 'templates'),
    static_folder=str(src_dir / 'static')
)

# Initialize LLM and Agent
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

# Store conversation history (in production, use a database or session storage)
chat_histories = {}


@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        session_id = data.get('session_id', 'default')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Get or create chat history for this session
        if session_id not in chat_histories:
            chat_histories[session_id] = []

        chat_history = chat_histories[session_id]

        logger.info(f"\n{'#'*60}")
        logger.info(f"📨 NEW USER MESSAGE: {user_message}")
        logger.info(f"{'#'*60}\n")
        # BREAKPOINT HERE: Set breakpoint on this line to see incoming messages

        # Invoke the agent with callbacks
        result = executor.invoke(
            {
                "input": user_message,
                "chat_history": chat_history
            },
            config={"callbacks": [ToolLoggingCallback()]}
        )
        # BREAKPOINT HERE: Set breakpoint on this line to see final results

        response_text = result["output"]
        logger.info(f"\n{'#'*60}")
        logger.info(f"🤖 AGENT RESPONSE: {response_text}")
        logger.info(f"{'#'*60}\n")

        # Update chat history
        from langchain_core.messages import HumanMessage, AIMessage
        chat_history.append(HumanMessage(content=user_message))
        chat_history.append(AIMessage(content=response_text))

        # Keep only last 10 messages to avoid context length issues
        if len(chat_history) > 10:
            chat_histories[session_id] = chat_history[-10:]

        return jsonify({
            'response': response_text,
            'status': 'success'
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear chat history for a session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        if session_id in chat_histories:
            chat_histories[session_id] = []

        return jsonify({'status': 'success', 'message': 'Chat history cleared'})

    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500


if __name__ == '__main__':
    # Disable reloader to avoid "No module named app" errors
    # The reloader has issues when running from different directories
    app.run(debug=True, host='0.0.0.0', port=9000, use_reloader=False)
