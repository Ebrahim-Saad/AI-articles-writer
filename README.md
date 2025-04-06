# AI Articles Writer

AI Articles Writer is a tool that automates the process of writing articles using AI. It searches for information online and generates structured articles with customizable sections.

## Installation

1. **Python**  
   Make sure you have Python **3.13** or later installed.

2. **Poetry**  
   Install [Poetry](https://python-poetry.org/docs/). If you are using **Poetry 1.2 or later**, it provides automatic virtual environment management.

3. **Clone this repository**  
   ```bash
   git clone https://github.com/Ebrahim-Saad/AI-articles-writer.git
   cd AI-articles-writer
   ```

4. **Install dependencies**  
   ```bash
   poetry install
   ```
   This installs all required dependencies from the `pyproject.toml`.

## Usage

1. **Set environment variables**  
   in the `.env` file you should add your own api keys for tavily and together, or adjust the file as you need if you wand to change the model used.

   **Note:** the model used is a free model together.ai offers, it's just for demo purpose, you have to adjust the model used later.
   don't forget to remove any delay's added to ensure not exceeding the api request limit for the free model to benefit from parellel writing.

2. **Activate the virtual environment** (optional in Poetry 1.2+):
   ```bash
   poetry shell
   ```

3. **Run the application**  
   ```bash
   poetry run aiarticleswriter
   ```
   Follow the on-screen prompts:
   - Enter your article topic.
   - Enter the target language.
   - Confirm or edit the AI-generated article plan.
   - Wait while the tool writes each section.
   - (Optional) Save your final article.

## Features

- **Automated Searching**: Gathers relevant information for your chosen topic.  
- **Customizable Outline**: Lets you edit the article sections before writing begins.  
- **Progress Feedback**: Displays a Rich progress bar during the article creation.  
- **Markdown Output**: Final article is displayed in Markdown and can be saved locally.  
- **Adjustable Language**: Specify the language for article content.  
- **Rich Integration**: Provides a stylized CLI with color-coded messages.

For more details or troubleshooting, please refer to code comments or open an issue in this repository.
