# src/web_app.py
"""
Web interface for Godot AI Development Assistant.
Provides HTTP API endpoints for chat functionality.

Refactored to use dependency injection for better testability and modularity.
"""
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify

from di_container import get_container
from commands import CommandContext, CommandError

# Initialize Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Global container (initialized on first request)
container = None


def get_or_create_container():
	"""
	Get or create the DI container.
	
	Lazy initialization on first request.
	
	Returns:
		The global DIContainer instance
	"""
	global container
	if container is None:
		container = get_container()
		
		# Initialize assistant
		assistant = container.get('assistant')
		assistant.load_or_create_vectorstore()
		assistant.setup_qa_chain()
		
		print("✓ Assistant initialized successfully")
	
	return container


@app.route('/')
def index():
	"""Render the main chat interface."""
	return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask_question():
	"""
	Handle question submission from the web interface.
	
	Returns:
		JSON response with answer or error
	"""
	try:
		# Get container and dependencies
		container = get_or_create_container()
		assistant = container.get('assistant')
		project_analyzer = container.get('project_analyzer')
		display_manager = container.get('output_manager')
		command_parser = container.get('command_parser')
		
		# Accept both JSON and form data
		if request.is_json:
			data = request.get_json()
			question = data.get('question', '').strip()
		else:
			question = request.form.get('question', '').strip()
		
		if not question:
			return jsonify({'error': 'Question cannot be empty'}), 400
		
		# Try to parse and execute as command
		try:
			command = command_parser.parse(question)
			if command:
				context = CommandContext(
					project_analyzer=project_analyzer,
					display_manager=display_manager,
					assistant=assistant
				)
				result = command.execute(context)
				
				# Determine command type from result
				cmd_type = _classify_command_result(result)
				
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
		
		# Not a command - process as regular question
		enhanced_question = _enhance_with_context(question, assistant)
		
		# Query the assistant
		result = assistant.qa_chain.invoke({"query": enhanced_question})
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
		container = get_or_create_container()
		config = container.get('config')
		assistant = container.get('assistant')
		
		return jsonify({
			'status': 'ready',
			'api_provider': config.api.provider,
			'embedding_provider': config.embedding.provider,
			'model': config.get_model_name(),
			'project_info': assistant.project_analyzer.get_project_info()
		})
	except Exception as e:
		return jsonify({
			'status': 'error',
			'error': str(e)
		}), 500


def _classify_command_result(result: str) -> str:
	"""
	Classify command result for appropriate frontend handling.
	
	Args:
		result: Command execution result string
		
	Returns:
		Classification type string
	"""
	result_lower = result.lower()
	
	if 'error' in result_lower or '❌' in result:
		return 'error'
	elif 'file' in result_lower and 'loaded' in result_lower:
		return 'file_content'
	elif 'files matching' in result_lower:
		return 'file_list'
	elif 'project' in result_lower:
		return 'project_info'
	elif 'lore' in result_lower:
		return 'lore_status'
	else:
		return 'success'


def _enhance_with_context(question: str, assistant) -> str:
	"""
	Enhance question with file context if available.
	
	Args:
		question: Original question
		assistant: Assistant instance
		
	Returns:
		Enhanced question with file context
	"""
	if not assistant.last_read_file:
		return question
	
	return f"""I previously read the file: {assistant.last_read_file['path']}

Here is the content of that file:
```
{assistant.last_read_file['content'][:4000]}
```

Now, my question is: {question}"""


if __name__ == '__main__':
	try:
		# Get container and configuration
		container = get_or_create_container()
		config = container.get('config')
		
		# Run Flask app with configured settings
		app.run(
			host=config.web.host,
			port=config.web.port,
			debug=config.web.debug
		)
	except ValueError as e:
		print(f"❌ Configuration error: {e}")
		print("\nPlease check your .env file and ensure all required settings are present.")
		exit(1)
	except KeyError as e:
		print(f"❌ Dependency injection error: {e}")
		print("\nPlease check that all dependencies are properly registered.")
		exit(1)