
from langchain.agents import initialize_agent

from langchain.agents.agent_types import AgentType

from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI # or ChatGoogleGenerativeAI if preferred
from os import getenv
from dotenv import load_dotenv
load_dotenv()



from Chat_YTube.yt_search import extract_search_topic_spacy, search_youtube,detect_tone_from_keywords
from Chat_YTube.yt_search import Extract_Query, SearchYTInput, DetectTone
from Ggen_llm import mood_map_llm, MoodInput

# ---------------------- LLM Handling ----------------------
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")

# -------------------- Tool Definitions --------------------
tool_extract_query = StructuredTool.from_function(
    func=extract_search_topic_spacy,
    args_schema= Extract_Query,
    infer_schema= True,
    name="ExtractQuery",
    description="Extracts the main search topic from the user's message."
)

tool_mood_map = StructuredTool.from_function(
    func=mood_map_llm,
    name="MoodMapper",
    args_schema=MoodInput,  # A Pydantic model with multiple fields
    description="Maps tone and returns uplifted YouTube search query."
)

tool_yt_search= StructuredTool.from_function(
    func= search_youtube,
    args_schema= SearchYTInput,
    infer_schema= True,
    name= "Youtube Searcher",
    description= "Finds the search query returned by mood_map_llm to be searched on YouTube to get Search Results"
)

llm_controller = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0.7
)

agent = initialize_agent(
    tools=[tool_extract_query, tool_mood_map],
    llm=llm_controller,
    agent= AgentType.OPENAI_MULTI_FUNCTIONS,
    verbose=True
)

# Handle new prompt
if prompt := input("💬 Type your prompt here: "):
    response = agent.run(prompt)
    print(response)
