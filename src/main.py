# src/main.py
"""
Console entry point for Godot AI Development Assistant.
Provides interactive CLI for querying the assistant.
"""
import sys
from config import load_config
from project_analyzer import ProjectAnalyzer
from godot_assistant import GodotAIAssistant
from console_output import ConsoleOutputManager


def initialize_chat(assistant: GodotAIAssistant, display_manager: ConsoleOutputManager) -> None:
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
		# Load and validate configuration
		config = load_config()
		
		# Initialize display manager
		display_manager = ConsoleOutputManager(config.language)
		display_manager.print_title()
		
		# Print configuration summary
		config.print_summary()

		# Initialize project analyzer
		project_analyzer = ProjectAnalyzer(config.paths.project_path)
		display_manager.print_project_status(project_analyzer)

		# Initialize assistant with configuration
		assistant = GodotAIAssistant(
			project_analyzer=project_analyzer,
			display_manager=display_manager,
			config=config
		)

		# Load or create vector database
		assistant.load_or_create_vectorstore()

		# Setup QA chain
		assistant.setup_qa_chain()
		
		# Start interactive chat
		initialize_chat(assistant, display_manager)

	except ValueError as e:
		print(f"❌ Configuration error: {e}")
		print("\nPlease check your .env file and ensure all required settings are present.")
		sys.exit(1)
	except Exception as e:
		print(f"❌ Fatal error: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()