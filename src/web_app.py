# src/web_app.py
"""
Web interface for Godot AI Development Assistant.
Provides HTTP API endpoints for chat functionality.
"""
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify

from config import load_config, AppConfig
from project_analyzer import ProjectAnalyzer
from godot_assistant import GodotAIAssistant
from console_output import ConsoleOutputManager
from commands import CommandParser, CommandContext, CommandError

# Initialize Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Global instances (initialized on first request)
assistant: GodotAIAssistant | None = None
project_analyzer: ProjectAnalyzer | None = None
display_manager: ConsoleOutputManager | None = None
config: AppConfig | None = None
command_parser: CommandParser | None = None


def get_assistant() -> GodotAIAssistant:
	"""
	Lazy initialization of the assistant and dependencies.
	
	Returns:
		Initialized GodotAIAssistant instance
		
	Raises:
		ValueError: If configuration is invalid
	"""
	global assistant, project_analyzer, display_manager, config, command_parser
	
	if assistant is None:
		# Load configuration
		config = load_config()
		config.print_summary()
		
		# Initialize display manager
		display_manager = ConsoleOutputManager(config.language)
		
		# Initialize project analyzer
		project_analyzer = ProjectAnalyzer(config.paths.project_path)
		
		# Initialize command parser
		command_parser = CommandParser()
		
		# Initialize assistant
		assistant = GodotAIAssistant(
			project_analyzer=project_analyzer,
			display_manager=display_manager,
			config=config
		)
		
		# Load or create vector database
		assistant.load_or_create_vectorstore()
		
		# Setup QA chain
		assistant.setup_qa_chain()
		
		print("✓ Assistant initialized successfully")
	
	return assistant


@app.route('/')
def index():
	"""Render the main chat interface"""
	return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask_question():
	"""
	Handle question submission from the web interface.
	
	Returns:
		JSON response with answer or error
	"""
	try:
		# Accept both JSON and form data
		if request.is_json:
			data = request.get_json()
			question = data.get('question', '').strip()
		else:
			question = request.form.get('question', '').strip()
		
		if not question:
			return jsonify({'error': 'Question cannot be empty'}), 400
		
		asst = get_assistant()
		
		# Try to parse and execute as command
		try:
			command = command_parser.parse(question)
			if command:
				context = CommandContext(
					project_analyzer=project_analyzer,
					display_manager=display_manager,
					assistant=asst
				)
				result = command.execute(context)
				
				# Determine command type from result
				if 'error' in result.lower() or '❌' in result:
					cmd_type = 'error'
				elif 'file' in result.lower() and 'loaded' in result.lower():
					cmd_type = 'file_content'
				elif 'files matching' in result.lower():
					cmd_type = 'file_list'
				elif 'project' in result.lower():
					cmd_type = 'project_info'
				elif 'lore' in result.lower():
					cmd_type = 'lore_status'
				else:
					cmd_type = 'success'
				
				return jsonify({
					'answer': result,
					'question': question,
					'type': cmd_type
				})
		except CommandError as e:
			return jsonify({
				'answer': f"❌ {str(e)}\nTip: Use /list to see available files",
				'question': question,
				'type': 'error'
			})
		
		# Not a command - process as regular question with context
		enhanced_question = question
		
		# If a file was recently read, include it in the context
		if asst.last_read_file:
			enhanced_question = f"""I previously read the file: {asst.last_read_file['path']}

Here is the content of that file:
```
{asst.last_read_file['content'][:4000]}
```

Now, my question is: {question}"""
		
		# Query the assistant
		result = asst.qa_chain.invoke({"query": enhanced_question})
		answer = result['result']
		
		return jsonify({
			'answer': answer,
			'question': question
		})
	
	except Exception as e:
		return jsonify({'error': str(e)}), 500


@app.route('/api/status')
def get_status():
	"""
	Get system status information.
	
	Returns:
		JSON response with system status or error
	"""
	try:
		asst = get_assistant()
		return jsonify({
			'status': 'ready',
			'api_provider': config.api.provider,
			'embedding_provider': config.embedding.provider,
			'model': config.get_model_name(),
			'project_info': asst.project_analyzer.get_project_info()
		})
	except Exception as e:
		return jsonify({
			'status': 'error',
			'error': str(e)
		}), 500


if __name__ == '__main__':
	try:
		# Load config to get web settings
		web_config = load_config()
		
		# Run Flask app with configured settings
		app.run(
			host=web_config.web.host,
			port=web_config.web.port,
			debug=web_config.web.debug
		)
	except ValueError as e:
		print(f"❌ Configuration error: {e}")
		print("\nPlease check your .env file and ensure all required settings are present.")
		exit(1)