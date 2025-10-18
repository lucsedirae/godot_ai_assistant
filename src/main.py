import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from project_analyzer import ProjectAnalyzer
from godot_assistant import GodotAIAssistant
from console_output import ConsoleOutputManager

# Constants
CONSOLE_LANG: str = 'en'

# Load environment vars
load_dotenv()

def main():
    display_manager = ConsoleOutputManager(CONSOLE_LANG)
    display_manager.print_welcome()
    
    # Set config
    config = {
        'api_provider': os.getenv("API_PROVIDER", "anthropic").lower(),
        'embedding_provider': os.getenv("EMBEDDING_PROVIDER", "local").lower(),
    }
    
    display_manager.print_config(config)
    
    try:
        # Initialize project analyzer
        project_path = Path(os.getenv("GODOT_PROJECT_PATH", "/app/project"))
        project_analyzer = ProjectAnalyzer(project_path)
        
        # Initialize assistant with dependency injection
        assistant = GodotAIAssistant(
            project_analyzer=project_analyzer,
            api_provider=config['api_provider'],
            embedding_provider=config['embedding_provider']
        )
        
        # Show project status
        print("\n" + "="*80)
        print("Project Status:")
        print("="*80)
        print(project_analyzer.get_project_info())
        print("="*80)
        
        # Load or create vector database
        assistant.load_or_create_vectorstore()
        
        # Setup QA chain
        assistant.setup_qa_chain()
        
        print("\n" + "="*80)
        print("Assistant ready! Ask me anything about Godot development or your game lore.")
        print("\nSpecial Commands:")
        print("  /project info      - Show your project details")
        print("  /project structure - Show project file tree")
        print("  /read <file>       - Read a file from your project")
        print("  /list [pattern]    - List files (e.g., /list *.gd)")
        print("  /lore              - Show lore files status")
        print("  quit or exit       - Exit the assistant")
        print("="*80 + "\n")
        
        # Interactive loop
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                assistant.ask(question)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue
    
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()