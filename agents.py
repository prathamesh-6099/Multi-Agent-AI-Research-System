import os
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Load API keys from environment or Streamlit secrets
def _get_secret(key: str) -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        return st.secrets[key]
    except Exception:
        return ""

def get_llm() -> ChatGoogleGenerativeAI:
    """Gets LLM dynamically, supporting runtime updates from session state."""
    api_key = ""
    try:
        if "google_api_key" in st.session_state and st.session_state["google_api_key"]:
            api_key = st.session_state["google_api_key"]
    except Exception:
        pass
        
    if not api_key:
        api_key = _get_secret("GOOGLE_API_KEY") or _get_secret("GEMINI_API_KEY")
        
    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Please set GOOGLE_API_KEY in the sidebar, environment, or secrets."
        )
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0)


#1st agent 
def build_search_agent():
    return create_agent(
        model = get_llm(),
        tools= [web_search]
    )

#2nd agent 

def build_reader_agent():
    return create_agent(
        model = get_llm(),
        tools = [scrape_url]
    )


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

# Lazy Chain wrapper to prevent eager LLM initialization at import time
class LazyChain:
    def __init__(self, prompt):
        self.prompt = prompt

    def invoke(self, input_dict, config=None, **kwargs):
        llm_instance = get_llm()
        chain = self.prompt | llm_instance | StrOutputParser()
        return chain.invoke(input_dict, config=config, **kwargs)

writer_chain = LazyChain(writer_prompt)

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = LazyChain(critic_prompt)
