import os
from data_loader import DataLoader
from project_analyzer import ProjectAnalyzer

COLOR_OK = '\033[92m' #Green
COLOR_END = '\033[0m' #End color span

class ConsoleOutputManager:
  def __init__(self, lang: str) -> None:
    self.lang = lang
    pass

  def get_string(self, string_name: str) -> str|None:
    loader = DataLoader('src/output/data/' + self.lang + '.json')
    return loader.get(string_name)

  def print_config(self, config: dict) -> None:
    print(f"\nUsing {config['api_provider'].upper()} API")
    print(f"Using {config['embedding_provider'].upper()} embeddings")

  def print_project_status(self, analyzer: ProjectAnalyzer) -> None:
    print("\n" + "="*80)
    print(COLOR_OK + "Project Status:" + COLOR_END)
    print("="*80)
    print(analyzer.get_project_info())
    print("="*80)
  
  def print_title(self) -> None:
    print("="*80)
    print(self.get_string('app_title'))
    print("="*80)

  def print_welcome_message(self) -> None:
    os.system('clear')
    print("\n" + "="*80)
    print(COLOR_OK)
    print("Assistant ready! Ask me anything about Godot development or your game lore.")
    print(COLOR_END)
    print("\nSpecial Commands:")
    print("  /project info      - Show your project details")
    print("  /project structure - Show project file tree")
    print("  /read <file>       - Read a file from your project")
    print("  /list [pattern]    - List files (e.g., /list *.gd)")
    print("  /lore              - Show lore files status")
    print("  quit or exit       - Exit the assistant")
    print("="*80 + "\n")