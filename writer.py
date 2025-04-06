import sys
import os
import random
import time
import json
import json_repair
import logging
import dotenv
import operator

from pydantic import BaseModel, Field
from typing import List, Dict, Annotated, TypedDict, Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from agents.search import search_for_information
from langchain_together import ChatTogether
from langchain_core.messages import SystemMessage
import langgraph.constants
import langgraph.graph
import langgraph.prebuilt

dotenv.load_dotenv()
console = Console()
logger = logging.getLogger(__name__)

progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.completed}/{task.total}"),
    TimeElapsedColumn(),
    console=console,
    transient=False,
)
progress_task = None  # Will be set in orchasterator once we know total sections

# Initialize language models
llm = ChatTogether(model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")

# Define models for article sections
class Section(BaseModel):
    name: str = Field(
        description="Name for this section of the article.",
    )
    description: str = Field(
        description="Brief overview of the main points to be covered in this section, with all information required.",
    )

class Sections(BaseModel):
    sections: List[Section] = Field(
        description="Sections of the article.",
    )

# Define state schemas
class State(TypedDict):
    headline: str          # Report topic
    information: str       # Information about the headline
    sections: List[Section]
    completed_sections: Annotated[List[str], operator.add]  # All workers write to this key
    final_report: str      # Final report

class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[List[str], operator.add]

def generate_plan(headline: str, information: str, edits: str = "") -> List[Dict]:
    """
    Generate a plan (list of sections) using the user’s headline, information, and any user edits.
    """
    system_content = """Generate a plan for the article.
The plan should be a list of sections with descriptions containing all
information that should be included in each section in the same language of the headline, without extra text.
Example:
[
  {"name": "Introduction", "description": "..."},
  {"name": "Body", "description": "..."},
  {"name": "Conclusion", "description": "..."}
]"""

    # If user provided edits, add them to the system prompt
    if edits.strip():
        system_content += f"\n\n[Note: The user requested these plan edits: {edits}]"

    messages = [
        SystemMessage(content=system_content),
        {"role": "human", "content": headline},
        {
            "role": "system",
            "content": f"Here is all information required to write the article:\n{information}"
        },
    ]
    
    out = llm.invoke(messages)
    repaired = json_repair.repair_json(out.content)
    sections = json.loads(repaired)



    return sections

def orchasterator(state: State):
    """Generate a plan and ask for user edits. If edits are provided, regenerate the plan."""
    # Initial plan
    sections = generate_plan(state["headline"], state["information"])
    
    # Loop to handle user edits
    progress.stop()
    while True:
        console.print(f"\n[bold green]--- Proposed Plan ---[/bold green]\n")
        for idx, section in enumerate(sections, 1):
            console.print(f"[bold]{idx}. {section['name']}[/bold]")
            console.print(f"   {section['description']}\n")

        if Confirm.ask("[bold yellow]Do you want to make any edits to this plan?[/bold yellow]"):
            user_edits = Prompt.ask("[bold]Please describe your edits[/bold]")
            sections = generate_plan(state["headline"], state["information"], edits=user_edits)
        else:
            break

    console.print(f"\n[bold magenta]Final Plan Accepted[/bold magenta]\n")
    
    # Display final plan sections
    for idx, section in enumerate(sections, 1):
        console.print(f"[bold]{idx}. {section['name']}[/bold]")
        console.print(f"   {section['description']}\n")

    console.print(f"\n[bold magenta]Starting Article Writing processy[/bold magenta]\n")
    # Initialize progress with the total number of sections
    global progress_task
    progress_task = progress.add_task("Writing sections...", total=len(sections))

    return {"sections": sections}

def writer_with_search(state: WorkerState, max_iterations: int = 2) -> Dict:
    """Write a section with revision loop (here only initial draft + search)"""
    section = state['section']
    section_name = section["name"]
    section_description = section["description"]

    # Search for information (simulated delay)
    time.sleep(random.randint(1, 3) * 60)
    information = search_for_information(
        content=section_description,
        language="english"
    )
    # print(f"{section_name} \nFound information: {information['structured_response'].details}")

    # Create initial section text
    messages = [
        SystemMessage(content="You are a writer, write a section in the same provided language."),
        {
            "role": "human",
            "content": (
                f"Write about {section_name}\n"
                f"Here is the information required to write the section:\n"
                f"{information['structured_response'].details}"
            ),
        },
    ]

    try:
        out = llm.invoke(messages)
    except Exception as e:
        logger.error(f"Error invoking LLM: {e}")
        time.sleep(random.randint(1, 3) * 60)
        return writer_with_search(state, max_iterations)

    content = out.content

    # Update progress for this completed section
    global progress_task
    if progress_task is not None:
        progress.update(progress_task, advance=1, description=f"\nCompleted section: {section_name}\n")

    return {"completed_sections": [content]}

def synthesizer(state: State):
    """Synthesize the full report from all completed sections"""
    completed_sections = state["completed_sections"]
    completed_report_sections = "\n\n---\n\n".join(completed_sections)
    return {"final_report": completed_report_sections}

def assign_workers(state: State):
    """Assign a worker to each section in the plan"""
    return [
        langgraph.constants.Send("writer", {"section": s})
        for s in state["sections"]
    ]

def build_writer_graph():
    orchasterator_writer_builder = langgraph.graph.StateGraph(State)
    
    orchasterator_writer_builder.add_node("orchasterator", orchasterator)
    orchasterator_writer_builder.add_node("writer", writer_with_search)
    orchasterator_writer_builder.add_node("synthesizer", synthesizer)
    
    orchasterator_writer_builder.add_edge(langgraph.graph.START, "orchasterator")
    orchasterator_writer_builder.add_conditional_edges("orchasterator", assign_workers, "writer")
    orchasterator_writer_builder.add_edge("writer", "synthesizer")
    orchasterator_writer_builder.add_edge("synthesizer", langgraph.graph.END)
    
    return orchasterator_writer_builder.compile()

writer_graph = build_writer_graph()

def write_article(headline: str, information: str):
    """
    Write a complete article based on headline and information,
    showing a progress bar for all sections being written.
    The user can also edit the plan before writing.
    """
    state = {
        "headline": headline,
        "information": information,
        "sections": [],
        "completed_sections": [],
        "final_report": "",
    }
    
    logger.info(f"Starting article writing for: {headline}")
    
    # Use the progress context so the bar displays properly
    with progress:
        result = writer_graph.invoke(state)
    
    logger.info("Article writing completed")
    print(result)
    return result