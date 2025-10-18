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
    display_manager.print_title()
    
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
        
        display_manager.print_project_status(project_analyzer)
        
        # Load or create vector database
        assistant.load_or_create_vectorstore()
        
        # Setup QA chain
        assistant.setup_qa_chain()
        
        display_manager.print_welcome_message()
        
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
                display_manager.print_goodbye_message()
                # print("\n\nGoodbye!")
                break
            except Exception as e:
                display_manager.print_error(e)
                continue
    
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()