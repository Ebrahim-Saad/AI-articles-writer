from langchain_together import ChatTogether
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import tool
from pydantic import BaseModel
from typing import List
import langgraph.prebuilt
import os
import dotenv
import logging
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.markdown import Markdown
from rich.console import Console

dotenv.load_dotenv()
console = Console()

# Initialize language models
llm = ChatTogether(model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")

# Define the Source model for information sources
class Source(BaseModel):
    source: str
    information_found: str

# Define authentication tool
@tool 
def authenticate_source(Authenticate_Source: Source):
    """Authenticate the source of the information
Args:
    Authenticate_Source (Source): Source to authenticate
    
    Source : source: str, summary: str

    Returns:
    dict: is_authentic: bool"""

    # Check if the source is authentic
    # ok = (input("Does this information found on the source authentic? (yes/no): ").strip().lower() == "yes")
    console.print(f"information found: \n {Authenticate_Source.information_found} \n")
    ok = Confirm.ask(
        f"Does this information found on the source {Authenticate_Source.source} authentic?",
        default=True,
    )
    return {"is_authentic": ok}

# Initialize search tools
search_tools = [TavilySearchResults(max_results=3), authenticate_source]

# Define search prompt template
search_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a searching expert, you have to search for information about the given content by optimizing search queries"),
    ("system", "you have to make sure that this source is authentic, if no you have to re search and optimize the search query to find another sources, \n"),
    ("system", "then return a prober headline and rephrase all detailes found in {language}, make it clear and comprehensive."),
    ("system", "don't use any tools other than search tool and authenticate tool."),
    ("human", "search for information about {content}"),
])

# Define search output schema
class search_output_schema(BaseModel):
    headline: str
    details: str
    sources: List[Source]

# Create the search agent
search_agent = langgraph.prebuilt.create_react_agent(
    model=llm, 
    tools=search_tools, 
    response_format=search_output_schema
)

def search_for_information(content: str, language: str = "english") -> dict:
    """
    Search for information about a given content in the specified language
    
    Args:
        content (str): The content to search for
        language (str): The language for the response, defaults to "english"
        
    Returns:
        dict: Contains the structured_response with headline, details, and sources
    """
    # Invoke the search agent with the search prompt
    console.print("\n[bold green]Searching for information...[/bold green]")
    result = search_agent.invoke(search_prompt.invoke({"content": content, "language": language}))
        
    return result