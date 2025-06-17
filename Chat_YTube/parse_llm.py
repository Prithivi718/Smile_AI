from os import getenv

from dotenv import load_dotenv


load_dotenv()

from langchain.prompts import PromptTemplate

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

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

GOOGLE_API_KEY= getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            api_key=GOOGLE_API_KEY,
            temperature=0.7
)


# Define PromptTemplate
template = f"""
        [Task Overview]
        You are a compassionate mood-matching agent. Your mission is to uplift and support the user emotionally—especially if they’re feeling sad, tired, or unmotivated. Always try to make the user feel better, smile, and receive content that boosts their vibe.
        
        [You Must]
        1. Detect the user's emotional tone from the `user_tone` variable.
        2. If the tone is very negative (like "sad", "tired", "angry", "bored"), gently show care (e.g., "Cheer up! You're stronger than you think 💪").
        3. Create a 3–6 word YouTube search query that reflects the mapped tone and the original query content.
        
        [Input Variables]
        - `search_query`: The user’s intent (e.g., "motive tamil songs", "funny sad clips").
        - `user_tone`: Detected tone from the original user message.
        - Use this tone uplift mapping to guide your output:
          {boost_tone_mapping_str}
        
        [What You Should Do]
        
        Step 1 – Tone Mapping:
        - If `user_tone` is in the tone mapping, map it to a better emotional state.
        - If not, infer a suitable positive alternative.
        - ❗ Never reduce the user's energy or happiness. Never map "happy" → "calm" or "excited" → "sad".
        
        Step 2 – Query Building:
        - Construct a concise and uplifting search query (3–6 words).
        - Include regional/cultural context if relevant (e.g., Tamil, Hindi).
        - Match the new tone’s energy (e.g., energetic, funny, motivational).
        
        [Output Format]
        Return this exact JSON object (no backticks, no explanation, no markdown):
        {{{{
          "detected_tone": "<user_tone>",
          "search_query": "<search_query>",
          "final_query": "<uplifted YouTube query>"
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


# print(mood_map_llm("Motive Tamil and English Songs"))
