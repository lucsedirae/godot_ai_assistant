# src/main.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from project_analyzer import ProjectAnalyzer
from godot_assistant import GodotAIAssistant
from console_output import ConsoleOutputManager

# Constants
CONSOLE_LANG: str = "en"
ENV_API_PROVIDER: str = "API_PROVIDER"
ENV_EMBEDDING_PROVIDER: str = "EMBEDDING_PROVIDER"
ENV_GODOT_PROJECT_PATH: str = "GODOT_PROJECT_PATH"

# Load environment vars
load_dotenv()

# Initialize managers
display_manager = ConsoleOutputManager(CONSOLE_LANG)

def initialize_chat(assistant: GodotAIAssistant):
    """
    Initialize chat loop.

    Args:
        assistant: Instance of the GodotAIAssistant class.
    """
    display_manager.print_welcome_message()
    
    while True:
        try:
            prompt = display_manager.get_string("your_question")
            question = input(prompt).strip()

            if question.lower() in ["quit", "exit", "q"]:
                display_manager.print_goodbye_message()
                break

            if not question:
                continue

            assistant.ask(question)

        except KeyboardInterrupt:
            display_manager.print_goodbye_message()
            break
        except Exception as e:
            display_manager.print_error(e)
            continue


def main():
    """Main entry point for the application."""
    display_manager.print_title()

    # Set config
    config = {
        "api_provider": os.getenv(ENV_API_PROVIDER, "anthropic").lower(),
        "embedding_provider": os.getenv(ENV_EMBEDDING_PROVIDER, "local").lower(),
    }

    display_manager.print_config(config)

    try:
        # Initialize project analyzer
        project_path = Path(os.getenv(ENV_GODOT_PROJECT_PATH, "/app/project"))
        project_analyzer = ProjectAnalyzer(project_path)

        # Initialize assistant with dependency injection
        assistant = GodotAIAssistant(
            project_analyzer=project_analyzer,
            display_manager=display_manager,
            api_provider=config["api_provider"],
            embedding_provider=config["embedding_provider"],
        )

        display_manager.print_project_status(project_analyzer)

        # Load or create vector database
        assistant.load_or_create_vectorstore()

        # Setup QA chain
        assistant.setup_qa_chain()
        
        initialize_chat(assistant)

    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()