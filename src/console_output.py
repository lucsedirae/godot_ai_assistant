# src/console_output.py
import os
from project_analyzer import ProjectAnalyzer
from constants import (
    APP_TITLE,
    APP_VERSION,
    APP_DESCRIPTION,
    COLOR_OK,
    COLOR_END,
    COLOR_ERROR,
)


class ConsoleOutputManager:
    """Manages console output and formatting for the Godot AI Development Assistant."""

    def __init__(self, lang: str) -> None:
        """
        Initialize the ConsoleOutputManager with a language.

        Args:
                lang: Language code for loading localized strings
        """
        self.lang = lang

    def print_error(self, error: Exception) -> None:
        """
        Print an error message in colored text.

        Args:
                error: The exception to display
        """
        print(f"{COLOR_ERROR}\nError: {error}{COLOR_END}")

    def print_error_doc_missing(self, docs_path: str) -> None:
        """
        Print error message when documentation is missing.

        Args:
                docs_path: Path where documentation should be located
        """
        help_message = f"""
Documentation path {docs_path} not found!
Please add Godot documentation to the godot_docs directory.

You can:
1. Clone Godot docs: git clone https://github.com/godotengine/godot-docs.git godot_docs
2. Or manually add .rst, .md, or .txt files to godot_docs/
		"""
        print(help_message)

    def print_goodbye_message(self) -> None:
        """Print a goodbye message when the user exits the application."""
        print(f"{COLOR_OK}\n\nGoodbye!{COLOR_END}")

    def print_project_status(self, analyzer: ProjectAnalyzer) -> None:
        """
        Print detailed project status information.

        Args:
                analyzer: ProjectAnalyzer instance containing project information
        """
        print("\n" + "=" * 80)
        print(COLOR_OK + "Project Status:" + COLOR_END)
        print("=" * 80)
        print(analyzer.get_project_info())
        print("=" * 80)

    def print_title(self) -> None:
        """Print the application title with colored formatting."""
        print("=" * 80)
        print(COLOR_OK)
        print(APP_TITLE)
        print("Version:", APP_VERSION)
        print(COLOR_END)
        print(APP_DESCRIPTION)
        print("=" * 80)

    def print_welcome_message(self) -> None:
        """Clear the screen and display the welcome message with available commands."""
        os.system("clear")
        separator = "=" * 80
        welcome_text = f"""
{separator}
{COLOR_OK}Assistant ready! Ask me anything about Godot development or your game lore.{COLOR_END}

Special Commands:
  /project info      - Show your project details
  /project structure - Show project file tree
  /read <file>       - Read a file from your project (loads into context)
  /list [pattern]    - List files (e.g., /list *.gd)
  /lore              - Show lore files status
  /clear             - Clear loaded file context
  quit or exit       - Exit the assistant
{separator}
		"""
        print(welcome_text)
