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
    "comedy": "comedy",
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
            [🧠 Task Overview]
                You are a STRICT mood-mapping assistant. Your job is to transform a YouTube search query based on the user's emotional tone to uplift their mood.
            
                You will receive:
                - `search_query` : The user's raw YouTube search text.  
                  You MUST detect the user's tone **only** from this text.
            
            [🔍 Tone Detection Logic]
            1. Detect emotional tone from `search_query` using keywords. Valid tones:
               {boost_tone_mapping_str}
            2. DO NOT ask the user for their tone.  
            3. DO NOT hallucinate extra emotions.  
            4. If tone cannot be confidently identified, default to `"happy"`.
            
            [⬆️ Uplift Mapping]
            Use this tone mapping dictionary to map the detected tone to a higher-energy one:
            {boost_tone_mapping_str}
            
            [🔧 Query Generation Instructions]
            - Based on the `search_query` and mapped tone, return a NEW 3–6 word YouTube search query that fits the uplifted mood.
            - Include cultural tags if present (e.g., "Tamil", "English").
            - Focus on making the query short, uplifting, and emotionally aligned.
            
            [⚠️ Critical Rules — DO NOT BREAK]
            - ❌ Do NOT explain what you are doing.
            - ❌ Do NOT respond with confirmations like "Okay, I'm doing that..."
            - ✅ Return ONLY the final JSON. Nothing else.
            - ❌ Do NOT use markdown or triple backticks.
            - ❌ Do NOT return partial or nested text.

            [Output – REQUIRED FORMAT]
            Return **only** this JSON object—no extra text, no backticks:
            
            {{{{
              "detected_tone": "<user_tone>",
              "search_query" : "<search_query>",
              "final_query"  : "<uplifted YouTube query>"
            }}}}
"""
prompt = PromptTemplate(input_variables=["search_query"], template=template)

# Chain is Prompt -> LLM
chain = prompt | llm


# Pydantic input schema for StructuredTool
class MoodInput(BaseModel):
    search_query: str


# Tool function that runs the chain and returns the string
def mood_map_llm(search_query: str) -> str:
    ai_msg = chain.invoke({"search_query": search_query})
    return ai_msg.content


tool = StructuredTool.from_function(
    func=mood_map_llm,
    name="MoodMapper",
    args_schema=MoodInput,  # A Pydantic model with multiple fields
    description="Maps tone and returns uplifted YouTube search query."
)

agent = initialize_agent(
    tools=[tool],
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    llm=llm,
    verbose=True
)

response= agent.run("Vadivelu comedy videos")
print(response)