from os import getenv

from dotenv import load_dotenv

load_dotenv()

from langchain.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from langchain.agents import initialize_agent

from langchain.agents.agent_types import AgentType

from langchain_core.tools import StructuredTool

# ------------------------ LLM Mood + Query Selection ------------------------
tone_keywords = {
    "bored": "funny",
    "tired": "energetic",
    "sad": "happy",
    "angry": "calm",
    "happy": "happy",
    "motivated": "motivated",
    "comedy": "funny",
    "action": "motivated",
    "dramatic": "light-hearted",
    "fun": "fun",
    "excited": "excited",
    "charming": "happy",
    "romantic": "light-hearted",
    "thriller": "fun",
    "educational": "inspiring",
    "spiritual": "calm",
    "motivational": "motivated",
    "inspiring": "motivated",
    "relaxed": "soothing",
    "fear": "light-hearted"
}
boost_tone_mapping_str = str(tone_keywords).replace("{", "{{").replace("}", "}}")

GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# Define PromptTemplate
template = f"""
        [Task Overview]
        You are a kind and emotionally-aware search assistant. The user gives a YouTube search query and their detected emotional tone.
        
        Your mission is to:
        1. Recognize the user’s current tone from the `user_tone` input.
        2. Match that tone with a better, uplifting tone using the mapping below.
        3. Always uplift — never reduce energy or positivity.
        4. Generate a 3–6 word YouTube search query that fits the mapped tone.
        
        [Tone Mapping Dictionary]
        Use this exact dictionary to transform the tone:
        {boost_tone_mapping_str}
        
        [Input]
        You will receive:
        - search_query: the raw user search idea (e.g., "funny sad scenes", "motive tamil songs").
        - user_tone: the emotional tone already detected from the user's message.
        
        [Rules]
        - 🔒 NEVER change or override the provided `user_tone`.
        - 🔒 Do NOT try to guess tone from `search_query` — it’s already extracted.
        - 🛡️ NEVER downgrade tone (e.g., from happy → sad, or energetic → calm).
        - ✅ If tone is already positive (like "motivated", "happy", "energetic"), keep it as is.
        
        [Steps]
        1. Lookup the mapped tone from the dictionary.
        2. Build a short YouTube search query (3–6 words) that matches this tone.
        3. Include cultural context if relevant (e.g., Tamil, Hindi).
        4. Add a brief motivating phrase ONLY IF the tone is very negative (like "sad", "bored", "tired").
        
        [Output]
        Return the following JSON ONLY — no extra text, no backticks, no markdown:
        {{{{
          "detected_tone": "<user_tone>",
          "search_query": "<search_query>",
          "final_query": "<uplifted YouTube query>"
        }}}}
"""

prompt = PromptTemplate(input_variables=["search_query", "user_tone"], template=template)

# Chain is Prompt -> LLM
chain = prompt | llm


# Pydantic input schema for StructuredTool
class MoodInput(BaseModel):
    search_query: str
    user_tone: str


# Tool function that runs the chain and returns the string
def mood_map_llm(search_query: str, user_tone: str) -> str:
    ai_msg = chain.invoke({"search_query": search_query, "user_tone": user_tone})
    return ai_msg.content


tool = StructuredTool.from_function(
    func=mood_map_llm,
    name="MoodMapper",
    args_schema=MoodInput,  # A Pydantic model with multiple fields
    description="Maps tone and returns uplifted YouTube search query."
)

agent = initialize_agent(
    tools=[tool],
    agent=AgentType.OPENAI_MULTI_FUNCTIONS,
    llm=llm,
    verbose=True
)

response= agent.run("Hey I'm so tired I want some energetic songs to hear")
print(response)