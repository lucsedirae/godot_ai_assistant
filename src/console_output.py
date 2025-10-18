import os
from data_loader import DataLoader
from project_analyzer import ProjectAnalyzer

COLOR_OK = '\033[92m' #Green
COLOR_END = '\033[0m' #End color span
COLOR_ERROR = '\033[96m' #Cyan

class ConsoleOutputManager:
  """Manages console output and formatting for the Godot AI Development Assistant."""
  
  def __init__(self, lang: str) -> None:
    """
    Initialize the ConsoleOutputManager with a language.
    
    Args:
        lang: Language code for loading localized strings
    """
    self.lang = lang
    pass

  def get_string(self, string_name: str) -> str|None:
    """
    Load a localized string from the language JSON file.
    
    Args:
        string_name: The key of the string to retrieve
        
    Returns:
        The localized string value, or None if not found
    """
    loader = DataLoader('src/output/data/' + self.lang + '.json')
    return loader.get(string_name)

  def print_config(self, config: dict) -> None:
    """
    Print the current API and embedding provider configuration.
    
    Args:
        config: Dictionary containing 'api_provider' and 'embedding_provider' keys
    """
    print(f"\nUsing {config['api_provider'].upper()} API")
    print(f"Using {config['embedding_provider'].upper()} embeddings")
  
  def print_error(self, error: Exception) -> None:
    """
    Print an error message in colored text.
    
    Args:
        error: The exception to display
    """
    print(f"{COLOR_ERROR}\nError: {error}{COLOR_END}")

  def print_goodbye_message(self) -> None:
    """Print a goodbye message when the user exits the application."""
    print(f"{COLOR_OK}\n\nGoodbye!{COLOR_END}")
  
  def print_project_status(self, analyzer: ProjectAnalyzer) -> None:
    """
    Print detailed project status information.
    
    Args:
        analyzer: ProjectAnalyzer instance containing project information
    """
    print("\n" + "="*80)
    print(COLOR_OK + "Project Status:" + COLOR_END)
    print("="*80)
    print(analyzer.get_project_info())
    print("="*80)
  
  def print_title(self) -> None:
    """Print the application title with colored formatting."""
    print("="*80)
    print(COLOR_OK)
    print(self.get_string('app_title'))
    print(COLOR_END)
    print("="*80)

  def print_welcome_message(self) -> None:
    """Clear the screen and display the welcome message with available commands."""
    os.system('clear')
    separator = "=" * 80
    welcome_text = f"""
{separator}
{COLOR_OK}Assistant ready! Ask me anything about Godot development or your game lore.{COLOR_END}

Special Commands:
  /project info      - Show your project details
  /project structure - Show project file tree
  /read <file>       - Read a file from your project
  /list [pattern]    - List files (e.g., /list *.gd)
  /lore              - Show lore files status
  quit or exit       - Exit the assistant
{separator}
"""
    print(welcome_text)