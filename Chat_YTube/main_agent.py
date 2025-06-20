# ------------------------- Basic IMPORTS ----------------------------------------

import eel, os
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel
# ------------------------- AGENT IMPORTS from Lang-Chain-Graph ----------------------------------------

from langchain.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, START, END

# ------------------------- TOOL IMPORTS from Modules ----------------------------------------

from .yt_search import extract_search_topic_spacy, detect_tone_from_keywords, search_youtube
from .agent_llm import mood_map_llm, chat_comapanion_agent, ChatAgent

# ------------------------- State Graph LangGraph ----------------------------------------
from typing_extensions import TypedDict
class State(TypedDict):
    user_query: str
    router: str
    chat_response: dict
    yt_response: dict

# ------------------------- General Agent Decider & Youtube Agent Handler ----------------------------------------

class YoutubeAgent(BaseModel):
    message: str


def agent_execute(state: State) -> dict:

    message= state["user_query"]
    query = extract_search_topic_spacy(message)

    # b) extract tone
    tone = detect_tone_from_keywords(message)
    print(f"Extract Query: {query}\nTone: {tone}")
    # c) call the Agno agent
    search_query = mood_map_llm(query, tone)
    print(f"Final query: {search_query}")
    yt_res = search_youtube(search_query)
    print(f"Youtube Search Results:\n{yt_res}")
    return {"yt_response": yt_res}

def chat_companion(state:State) ->dict:
    message= state["user_query"]
    bot_response= chat_comapanion_agent(message)
    return {'chat_response': bot_response}

# ------------------------- Tool Creation ----------------------------------------
yt_tool = StructuredTool.from_function(
    name="youtube_agent",
    description="This tool performs an Youtube search for the User by Extracting the Query and Tone from the User Prompt and then generates a 'search_query' which searches the 'search_query' on Youtube ",
    args_schema=YoutubeAgent,
    func=agent_execute
)

chat_tool = StructuredTool.from_function(
    name="chat_companion",
    description="This tool is used like a Chat-Bot, a friendly conversation agent to chat with the user",
    args_schema=ChatAgent,
    func=chat_comapanion_agent
)



# ------------------------- Lang-Chain for Tools and Lang-Graph for Main Agent ----------------------------------------

GOOGLE_API_KEY = "<api-key>"

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0.7
)

template = """
        You are Jarvis, an AI assistant with access to two tools:
        
        - YouTubeAgent: For any queries related to searching YouTube for videos, songs, music, or media content.
        - ChatCompanion: For general questions, conversation, emotional support, or friendly advice.
        
        Your task is simple:
        🔍 Read the user input and decide which tool is most appropriate to handle it.
        
        ⚠️ Rules:
        - Respond with only one of the following tool names:
            • "YouTubeAgent"
            • "ChatCompanion"
        - Return nothing else. No explanation. No formatting. No markdown. No backticks.
        
        User input: {user_input}
"""


prompt = PromptTemplate(template=template, input_variables=["user_input"])

# 1) Build your agent as before
selector_chain= prompt | llm

def decider_agent(state: State) -> dict:
    user_q = state["user_query"]

    # 2) Instead of run(), call .plan()
    # It returns an AgentAction with tool name + input
    action = selector_chain.invoke({"user_input": user_q}).content
    # data = json.loads(action)

    # 3) stash just the router key
    return {"router": action.lower()}


# Build workflow
workflow = StateGraph(State)
workflow.add_node("action", decider_agent)
workflow.add_node("chat_bot", chat_companion)
workflow.add_node("youtube_search", agent_execute)

# Connect Edges
# If router == "chat", go to chat_companion
workflow.add_edge(START, "action")
workflow.add_conditional_edges(
    "action",
    lambda state: state["router"],  # <– this reads the 'router' value returned by decider_agent
    {
        "youtubeagent": "youtube_search",
        "chatcompanion": "chat_bot"
    }
)
# Both tool nodes terminate the flow
workflow.add_edge("chat_bot", END)     # None means “end”
workflow.add_edge("youtube_search", END)

flow_start= workflow.compile()


@eel.expose
def chain_start(message: str) -> dict:
    chain = flow_start.invoke({"user_query": message})
    router = chain.get("router")

    if router == "chatcompanion":
        return {
            "tool": "chatcompanion",
            "content": chain.get("chat_response", {})
        }

    elif router == "youtubeagent":
        return {
            "tool": "youtubeagent",
            "content": chain.get("yt_response", [])
        }

    # Optional fallback
    return {
        "tool": "unknown",
        "content": {"message": "Something went wrong or unknown tool used."}
    }

#print(chain_start("Hey I'm tired can you just fetch some songs for me"))