# src/main.py
"""
Console entry point for Godot AI Development Assistant.
Provides interactive CLI for querying the assistant.

Refactored to use dependency injection for better testability and modularity.
"""
import sys
from di_container import get_container, reset_container


def initialize_chat(assistant, display_manager) -> None:
    """
    Initialize and run the interactive chat loop.

    Args:
            assistant: Instance of the GodotAIAssistant class
            display_manager: Instance for managing console output
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


def main() -> None:
    """Main entry point for the console application."""
    try:
        # Get the DI container (initializes all dependencies)
        container = get_container()

        # Retrieve dependencies from container
        config = container.get("config")
        display_manager = container.get("output_manager")
        project_analyzer = container.get("project_analyzer")
        assistant = container.get("assistant")

        # Display startup information
        display_manager.print_title()
        config.print_summary()
        display_manager.print_project_status(project_analyzer)

        # Initialize vector database
        assistant.load_or_create_vectorstore()

        # Setup QA chain
        assistant.setup_qa_chain()

        # Start interactive chat
        initialize_chat(assistant, display_manager)

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print(
            "\nPlease check your .env file and ensure all required settings are present."
        )
        sys.exit(1)
    except KeyError as e:
        print(f"❌ Dependency injection error: {e}")
        print("\nPlease check that all dependencies are properly registered.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        reset_container()


if __name__ == "__main__":
    main()
