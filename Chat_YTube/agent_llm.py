# ------------------------ mood_matcher_agent.py ------------------------
import os, json
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.reasoning import ReasoningTools
from textwrap import dedent
from dotenv import load_dotenv
load_dotenv()

from pydantic import  BaseModel

# 1. Tone Keywords
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

# 2. Inline mapping into prompt, escaping braces for f‑string
escaped_map = str(tone_keywords).replace("{", "{{").replace("}", "}}")

# 3. Build your Agno agent
OPENROUTER_API_KEY = "<api-key>"

MoodMatcherAgent = Agent(
    name="Mood Matcher",
    role="Transforms a search query based on user tone to uplift mood.",
    model=OpenRouter(id="openai/gpt-4o-mini", api_key=OPENROUTER_API_KEY),
    instructions=dedent(f"""
        [Task Overview]
        You receive two inputs:
          • search_query: the user’s raw YouTube search text (e.g., "motive tamil songs").
          • user_tone   : the emotional state you’ve detected (e.g., "tired", "sad").

        Your job:
        1) Take the exact `user_tone` provided—do NOT re‑detect or override it.
        2) Map that tone to a more uplifting tone using this mapping:
           {escaped_map}
        3) Generate a concise 3–6 word YouTube search query matching the uplifted tone.
           – Include any cultural tags already present (e.g., “Tamil”).
        4) NEVER downgrade energy (e.g., avoid “happy” → “calm”).

        [Output Format]
        Return exactly this JSON (no extra text, no markdown, no backticks):
        {{{{
          "detected_tone": "<user_tone>",
          "search_query": "<search_query>",
          "final_query": "<uplifted search query>"
        }}}}
    """),
    tools=[ReasoningTools(think=True, analyze=True)],
    debug_mode=False,
    show_tool_calls=False
)

def mood_map_llm(search_query: str, user_tone: str) -> dict:
    """
    Wrapper around the Agno agent. Pass in both args, get back JSON as dict.
    """
    # Format the two inputs into a single prompt string
    resp= MoodMatcherAgent.run(f"search_query: {search_query}\nuser_tone: {user_tone}")
    raw_json_str = resp.content  # this is your JSON text
    data = json.loads(raw_json_str)
    return data["final_query"]


class ChatAgent(BaseModel):
    message: str


def chat_comapanion_agent(message: str) -> dict:
  chat_agent = Agent(
      name="Reasoning Agent",
      role="Logical problem solver that breaks tasks into clear reasoning steps.",

      model=OpenRouter(id="openai/gpt-4o-mini", api_key=OPENROUTER_API_KEY),

      description = "This agent serves as a kind, supportive chat companion — responding in a human-like, thoughtful, and natural way.",

      instructions = dedent(f"""
        Step-1]
          Carefully understand the user's message and intent from {{{{message}}}}. 
          Think deeply about what they might be feeling, needing, or hoping for.
          Use reasoning to decide how to best provide a helpful, supportive, or friendly reply.

        [Step-2]
          Craft your response in natural, conversational language.
          You may use casual phrasing, light humor, or emojis when appropriate — aim to feel like a human chat buddy.
          Always be respectful, positive, and kind.
          If the user’s message is formal, match that tone.
          If the user’s message is casual or emotional, respond in a warm, friendly way.

        Avoid robotic or repetitive phrasing. Be creative and genuine in your replies.
        [Output Format]
        Return exactly this JSON (no extra text, no markdown, no backticks):
        {{{{
          "response": <Your response for `user_message`?
        }}}}
      """),

      tools=[ReasoningTools
        (
          think=True,
          analyze=True,
        )
      ],
      debug_mode=False,
      show_tool_calls=False,

  )

  chat_response= chat_agent.run(f"Response friendly for message: {message}")
  raw_json_str = chat_response.content  # this is your JSON text
  data = json.loads(raw_json_str)
  return data["response"]

#print(chat_comapanion_agent("I'm so bored, help me to cheerup!"))