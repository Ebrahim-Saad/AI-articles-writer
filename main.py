import requests
import json
import argparse
import os
import sys
import time
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

# Add the server directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from agents.search import search_for_information
from agents.writer import write_article

console = Console()

def display_title():
    """Display application title"""
    console.print(Panel.fit(
        "[bold blue]AI Articles Writer[/bold blue]", 
        border_style="green"
    ))

def get_content():
    """Get the article headline from the user"""
    content = Prompt.ask("[bold]Enter the content you need to write about[/bold]")
    return content

def get_language():
    """Get the desired language for the article"""
    language = Prompt.ask(
        "[bold]Enter the language for your article[/bold]", 
        default="english"
    )
    return language

def search_information(content: str, language: str) -> Dict:
    """Search for information about the headline"""
    result = search_for_information(content=content, language=language)
    
    return result

def display_search_results(results: Dict):
    """Display the search results"""
    console.print("\n[bold green]Search Results:[/bold green]")
    console.print(f"[bold]Headline:[/bold] {results['structured_response'].headline}")
    
    # Display sources
    console.print("\n[bold]Sources:[/bold]")
    for i, source in enumerate(results["structured_response"].sources, 1):
        console.print(f"[bold]Source {i}:[/bold] {source.source}")
        console.print(f"[italic]{results['structured_response'].details}[/italic]\n")
    
    # Display details in a panel
    details_md = Markdown(results['structured_response'].details)
    console.print(Panel(
        details_md,
        title="[bold]Information Details[/bold]",
        border_style="blue",
        expand=False
    ))
    
    # Return the processed information for the article writing
    return {
        "headline": results['structured_response'].headline,
        "information": results['structured_response'].details
    }

def write_article_process(headline: str, information: str):
    """Process the article writing with progress updates"""
    console.print("\n[bold green]Planning for  Article Generation Process[/bold green]")
    
    result = write_article(headline, information)
    
    return result

def display_article(result: Dict):
    """Display the final article"""
    console.print("\n[bold green]Article Generation Complete![/bold green]")
    
    # Display the final article in a markdown panel
    article_md = Markdown(result["final_report"])
    console.print(Panel(
        article_md,
        title=f"[bold]{result.get('headline', 'Generated Article')}[/bold]",
        border_style="green",
        expand=False
    ))
    
    return result["final_report"]

def save_article(article_text: str, headline: str):
    """Save the article to a file"""
    if Confirm.ask("[bold]Would you like to save this article to a file?[/bold]"):
        # Create a filename from the headline
        filename = f"{headline.replace(' ', '_').lower()[:30]}.md"
        directory = "generated_articles"
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        filepath = os.path.join(directory, filename)
        
        with open(filepath, "w") as f:
            f.write(article_text)
            
        console.print(f"[bold green]Article saved to:[/bold green] {filepath}")

def main():
    """Main application flow"""
    display_title()
    
    # Get user input
    content = get_content()
    language = get_language()
    
    # Search for information
    search_results = search_information(content, language)
    processed_info = display_search_results(search_results)
    
    if Confirm.ask("[bold]Would you like to generate an article based on this information?[/bold]"):
        # Generate the article
        article_result = write_article_process(
            processed_info["headline"], 
            processed_info["information"]
        )
        
        # Display and save the article
        article_text = display_article(article_result)
        save_article(article_text, processed_info["headline"])
    
    console.print("[bold blue]Thank you for using the articles writer![/bold blue]")

if __name__ == "__main__":
    main()