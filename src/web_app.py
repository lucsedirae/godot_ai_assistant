import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from project_analyzer import ProjectAnalyzer
from godot_assistant import GodotAIAssistant
from console_output import ConsoleOutputManager

# Load environment variables
load_dotenv()

# Initialize Flask app with explicit template folder
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Constants
CONSOLE_LANG = "en"
ENV_API_PROVIDER = "API_PROVIDER"
ENV_EMBEDDING_PROVIDER = "EMBEDDING_PROVIDER"
ENV_GODOT_PROJECT_PATH = "GODOT_PROJECT_PATH"

# Initialize managers
display_manager = ConsoleOutputManager(CONSOLE_LANG)

# Global assistant instance (initialized on first request)
assistant = None
project_analyzer = None
last_read_file = None  # Track the last file that was read

def get_assistant():
    """Lazy initialization of the assistant"""
    global assistant, project_analyzer
    
    if assistant is None:
        config = {
            "api_provider": os.getenv(ENV_API_PROVIDER, "anthropic").lower(),
            "embedding_provider": os.getenv(ENV_EMBEDDING_PROVIDER, "local").lower(),
        }
        
        # Initialize project analyzer
        project_path = Path(os.getenv(ENV_GODOT_PROJECT_PATH, "/app/project"))
        project_analyzer = ProjectAnalyzer(project_path)
        
        # Initialize assistant
        assistant = GodotAIAssistant(
            project_analyzer=project_analyzer,
            display_manager=display_manager,
            api_provider=config["api_provider"],
            embedding_provider=config["embedding_provider"],
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
    """Handle question submission"""
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
        
        # Handle special commands
        if question.lower().startswith('/project'):
            return handle_project_command(question)
        elif question.lower().startswith('/read '):
            return handle_read_file(question)
        elif question.lower().startswith('/list'):
            return handle_list_files(question)
        elif question.lower().startswith('/lore'):
            return handle_lore_command()
        elif question.lower() == '/clear':
            return handle_clear_context()
        
        # Regular question
        enhanced_question = question
        
        # If a file was recently read, include it in the context
        if last_read_file:
            enhanced_question = f"""I previously read the file: {last_read_file['path']}

Here is the content of that file:
```
{last_read_file['content'][:4000]}
```

Now, my question is: {question}"""
        
        answer = asst.ask(enhanced_question)
        
        return jsonify({
            'answer': answer,
            'question': question
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handle_project_command(command):
    """Handle project-related commands"""
    asst = get_assistant()
    
    if "info" in command.lower():
        info = asst.project_analyzer.get_project_info()
        return jsonify({
            'answer': f"<pre>{info}</pre>",
            'question': command,
            'type': 'project_info'
        })
    elif "structure" in command.lower():
        structure = asst.project_analyzer.get_project_structure()
        return jsonify({
            'answer': f"<pre>{structure}</pre>",
            'question': command,
            'type': 'project_structure'
        })
    else:
        commands = """Available project commands:
- /project info      - Show project information
- /project structure - Show project file structure
- /read <file>       - Read a specific file
- /list [pattern]    - List files (default: *.gd)
- /lore              - Show lore files status"""
        return jsonify({
            'answer': f"<pre>{commands}</pre>",
            'question': command,
            'type': 'help'
        })

def handle_read_file(command):
    """Handle file reading command"""
    global last_read_file
    
    asst = get_assistant()
    file_path = command[6:].strip()
    
    content = asst.project_analyzer.read_file(file_path)
    
    if content is None:
        last_read_file = None
        return jsonify({
            'answer': f"❌ File not found: {file_path}\nTip: Use /list to see available files",
            'question': command,
            'type': 'error'
        })
    
    # Store the file content for context
    last_read_file = {
        'path': file_path,
        'content': content
    }
    
    # Limit display for web
    display_content = content[:3000]
    if len(content) > 3000:
        display_content += f"\n\n... (showing first 3000 chars of {len(content)} total)"
    
    return jsonify({
        'answer': f"<pre>📄 Contents of {file_path}:\n{'='*80}\n{display_content}\n{'='*80}\n\nFile loaded! You can now ask questions about this file.</pre>",
        'question': command,
        'type': 'file_content'
    })

def handle_list_files(command):
    """Handle file listing command"""
    asst = get_assistant()
    pattern = command[5:].strip() or "*.gd"
    
    files = asst.project_analyzer.find_files(pattern)
    
    if not files:
        return jsonify({
            'answer': f"❌ No files found matching: {pattern}",
            'question': command,
            'type': 'error'
        })
    
    file_list = "\n".join([f"  {f}" for f in files[:50]])
    if len(files) > 50:
        file_list += f"\n\n... and {len(files) - 50} more"
    
    return jsonify({
        'answer': f"<pre>📁 Files matching '{pattern}':\n{'='*80}\n{file_list}\n{'='*80}</pre>",
        'question': command,
        'type': 'file_list'
    })

def handle_lore_command():
    """Handle lore status command"""
    asst = get_assistant()
    lore_path = Path("/app/data/lore")
    
    result = ["Lore Status:", "="*80]
    
    if not lore_path.exists():
        result.append(f"❌ Lore directory not found: {lore_path}")
        result.append("Create the directory and add .txt, .md, or .rst files")
    else:
        result.append(f"✓ Lore directory: {lore_path}")
        
        lore_files = []
        for pattern in ["*.txt", "*.md", "*.rst"]:
            lore_files.extend(list(lore_path.rglob(pattern)))
        
        if lore_files:
            result.append(f"✓ Found {len(lore_files)} lore files:")
            for f in lore_files:
                rel_path = f.relative_to(lore_path)
                size = f.stat().st_size
                result.append(f"  - {rel_path} ({size:,} bytes)")
        else:
            result.append("⚠ No lore files found")
            result.append("Add .txt, .md, or .rst files to the lore directory")
    
    result.append("="*80)
    
    return jsonify({
        'answer': f"<pre>{chr(10).join(result)}</pre>",
        'question': '/lore',
        'type': 'lore_status'
    })

def handle_clear_context():
    """Clear the last read file context"""
    global last_read_file
    
    if last_read_file:
        file_path = last_read_file['path']
        last_read_file = None
        return jsonify({
            'answer': f"✓ Cleared file context for: {file_path}",
            'question': '/clear',
            'type': 'success'
        })
    else:
        return jsonify({
            'answer': "No file context to clear.",
            'question': '/clear',
            'type': 'info'
        })

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        asst = get_assistant()
        return jsonify({
            'status': 'ready',
            'api_provider': asst.api_provider,
            'embedding_provider': asst.embedding_provider,
            'project_info': asst.project_analyzer.get_project_info()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Run in development mode
    app.run(host='0.0.0.0', port=5000, debug=True)