from langchain_groq import ChatGroq # type: ignore
from langchain.agents import AgentExecutor, create_react_agent # type: ignore
from langchain_community.chat_message_histories import ChatMessageHistory # type: ignore
from langchain_core.chat_history import BaseChatMessageHistory # type: ignore
from langchain import hub # type: ignore
from dotenv import load_dotenv # type: ignore
import os

from agent.tools import all_tools

load_dotenv()

# ---------------------------------------------------------------------------
# In-memory store for conversation history (per session)
# ---------------------------------------------------------------------------
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


def build_agent() -> AgentExecutor:
    """
    Builds and returns a ReAct AgentExecutor with:
    - Groq LLM (llama3-8b-8192)
    - Custom EduGuide tools
    - Conversation memory so context persists across turns
    """

    # 1. LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=os.getenv("GROQ_API_KEY"),
    )

    # 2. Pull the standard ReAct prompt from LangChain Hub
    #    This gives the agent its "Thought → Action → Observation" reasoning loop
    prompt = hub.pull("hwchase17/react")

    # 3. Create the ReAct agent (links LLM + tools + prompt together)
    agent = create_react_agent(
        llm=llm,
        tools=all_tools,
        prompt=prompt,
    )

    # 4. Wrap in AgentExecutor — this is what actually runs the think/act loop
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,           # prints agent's reasoning steps to terminal
        handle_parsing_errors=True,
        max_iterations=5,       # safety cap to prevent infinite loops
    )

    return agent_executor
