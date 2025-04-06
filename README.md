# AI Articles Writer

AI Articles Writer is a tool that automates the process of writing articles using AI. It searches for information online and generates structured articles with customizable sections.

## Installation

1. Ensure you have Python 3.13 or later.
2. Install [Poetry](https://python-poetry.org/docs/).
3. Clone this repository or download the files into a folder.
4. In the project directory, run:
   ```bash
   poetry install
   ```
   This will create a virtual environment and install all dependencies listed in the `pyproject.toml` file.

## Usage

1. Activate the project’s virtual environment:
   ```bash
   poetry shell
   ```
2. Run the main script:
   ```bash
   poetry run aidocumenthelper
   ```
3. Follow the on-screen prompts:
   - Enter the topic (content) for your article.
   - Enter the target language.
   - Confirm or edit the AI-generated plan (sections).
   - Wait while the tool writes each section.
   - (Optional) Save the final article to disk.

## Features

- **Automated Searching**: Uses a search agent to gather relevant information about the topic.
- **Customizable Outline**: Offers a plan for the article and lets you edit/add/remove sections before writing begins.
- **Progress Feedback**: Displays a Rich progress bar showing the sections being written.
- **Markdown Output**: Final article is displayed with Markdown formatting and can be saved locally.
- **Adjustable Language**: Allows specifying the language for the article content.
- **Integration with Rich**: Provides a more readable, stylized CLI experience with color-coded messages.

For more details or troubleshooting, please refer to the code comments or raise an issue on the repository.