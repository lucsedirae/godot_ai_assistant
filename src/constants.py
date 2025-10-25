# src/constants.py
"""
Centralized constants for Godot AI Development Assistant.
All magic strings, numbers, and configuration defaults are defined here.
"""
from pathlib import Path

# =============================================================================
# API Configuration Constants
# =============================================================================
API_PROVIDER_ANTHROPIC = "anthropic"
API_PROVIDER_OPENAI = "openai"
VALID_API_PROVIDERS = [API_PROVIDER_ANTHROPIC, API_PROVIDER_OPENAI]

# =============================================================================
# Embedding Configuration Constants
# =============================================================================
EMBEDDING_PROVIDER_LOCAL = "local"
EMBEDDING_PROVIDER_OPENAI = "openai"
VALID_EMBEDDING_PROVIDERS = [EMBEDDING_PROVIDER_LOCAL, EMBEDDING_PROVIDER_OPENAI]

# =============================================================================
# Model Names
# =============================================================================
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
DEFAULT_OPENAI_MODEL = "gpt-4-turbo-preview"
DEFAULT_HUGGINGFACE_MODEL = "all-MiniLM-L6-v2"

# =============================================================================
# LLM Configuration
# =============================================================================
DEFAULT_LLM_TEMPERATURE = 0
DEFAULT_DEVICE = "cpu"

# =============================================================================
# RAG Configuration Constants
# =============================================================================
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_RETRIEVAL_K = 6

# =============================================================================
# Web Server Configuration
# =============================================================================
DEFAULT_WEB_HOST = "0.0.0.0"
DEFAULT_WEB_PORT = 5000
DEFAULT_WEB_DEBUG = True

# =============================================================================
# Path Configuration
# =============================================================================
DEFAULT_PROJECT_PATH = "/app/project"
DEFAULT_DOCS_PATH = "/app/godot_docs"
DEFAULT_LORE_PATH = "/app/data/lore"
DEFAULT_DB_PATH = "/app/data/chroma_db"

# =============================================================================
# Language/Localization
# =============================================================================
DEFAULT_LANGUAGE = "en"
LANGUAGE_DATA_PATH_TEMPLATE = "src/output/data/{lang}.json"

# =============================================================================
# File Extensions
# =============================================================================
GODOT_SCRIPT_EXTENSION = "*.gd"
GODOT_SCENE_EXTENSION = "*.tscn"
GODOT_RESOURCE_EXTENSION = "*.tres"
GODOT_PROJECT_FILE = "project.godot"

# Document file extensions
TEXT_EXTENSIONS = ["*.txt", "*.md", "*.rst"]
DOC_EXTENSION_RST = "**/*.rst"

# =============================================================================
# Console Output Colors
# =============================================================================
COLOR_OK = "\033[92m"  # Green
COLOR_END = "\033[0m"  # End color span
COLOR_ERROR = "\033[96m"  # Cyan

# =============================================================================
# Display Limits
# =============================================================================
MAX_FILE_CONTENT_DISPLAY = 3000
MAX_FILE_CONTENT_CONTEXT = 4000
MAX_FILES_PER_DIRECTORY = 10
MAX_FILES_IN_LIST = 50
MAX_STRUCTURE_LINES = 100
MAX_STRUCTURE_DEPTH = 3

# =============================================================================
# Command Prefixes
# =============================================================================
COMMAND_PREFIX = "/"
COMMAND_PROJECT = "/project"
COMMAND_READ = "/read"
COMMAND_LIST = "/list"
COMMAND_LORE = "/lore"
COMMAND_CLEAR = "/clear"

# Command subcommands
SUBCOMMAND_INFO = "info"
SUBCOMMAND_STRUCTURE = "structure"

# =============================================================================
# Exit Commands
# =============================================================================
EXIT_COMMANDS = ["quit", "exit", "q"]

# =============================================================================
# Metadata Keys
# =============================================================================
METADATA_SOURCE_TYPE = "source_type"
SOURCE_TYPE_DOCUMENTATION = "documentation"
SOURCE_TYPE_LORE = "lore"

# =============================================================================
# Separator Characters
# =============================================================================
SEPARATOR_LINE = "=" * 80
SEPARATOR_SHORT = "=" * 40

# =============================================================================
# Environment Variable Names
# =============================================================================
ENV_API_PROVIDER = "API_PROVIDER"
ENV_ANTHROPIC_KEY = "ANTHROPIC_API_KEY"
ENV_OPENAI_KEY = "OPENAI_API_KEY"
ENV_EMBEDDING_PROVIDER = "EMBEDDING_PROVIDER"
ENV_GODOT_PROJECT_PATH = "GODOT_PROJECT_PATH"
ENV_ANTHROPIC_MODEL = "ANTHROPIC_MODEL"
ENV_OPENAI_MODEL = "OPENAI_MODEL"
ENV_LLM_TEMPERATURE = "LLM_TEMPERATURE"
ENV_RAG_CHUNK_SIZE = "RAG_CHUNK_SIZE"
ENV_RAG_CHUNK_OVERLAP = "RAG_CHUNK_OVERLAP"
ENV_RAG_RETRIEVAL_K = "RAG_RETRIEVAL_K"
ENV_WEB_HOST = "WEB_HOST"
ENV_WEB_PORT = "WEB_PORT"
ENV_WEB_DEBUG = "WEB_DEBUG"
ENV_LANGUAGE = "LANGUAGE"

# =============================================================================
# LangChain Configuration
# =============================================================================
CHAIN_TYPE_STUFF = "stuff"
LENGTH_FUNCTION = len

# =============================================================================
# QA Prompt Template
# =============================================================================
QA_PROMPT_TEMPLATE = """You are an expert Godot game engine assistant with access to:
1. Official Godot documentation
2. Game/project lore and world-building documents
3. The user's actual project files

IMPORTANT CAPABILITIES:
- You can read files from the user's project by asking them to share specific file paths
- You can see the project structure when provided
- You have access to lore documents that describe the game's world, characters, story, and setting
- You should provide advice tailored to their specific project when relevant

When answering questions about lore, story, characters, or world-building:
- Use the lore documents provided in the context
- Be specific and reference details from the lore
- Help maintain consistency with established lore

When answering technical Godot questions:
- Use the Godot documentation in the context
- Provide specific code examples using GDScript syntax
- Reference best practices

If you don't know the answer based on the context provided, just say that you don't know - don't make up information.

Context (may include documentation and/or lore):
{context}

Question: {question}

Helpful Answer:"""

QA_PROMPT_INPUT_VARIABLES = ["context", "question"]

# =============================================================================
# File Context Enhancement Template
# =============================================================================
FILE_CONTEXT_TEMPLATE = """I previously read the file: {file_path}

Here is the content of that file:
```
{file_content}
```

Now, my question is: {question}"""

# =============================================================================
# HTTP Status Messages
# =============================================================================
STATUS_READY = "ready"
STATUS_ERROR = "error"

# =============================================================================
# Command Response Types
# =============================================================================
RESPONSE_TYPE_SUCCESS = "success"
RESPONSE_TYPE_ERROR = "error"
RESPONSE_TYPE_INFO = "info"
RESPONSE_TYPE_FILE_CONTENT = "file_content"
RESPONSE_TYPE_FILE_LIST = "file_list"
RESPONSE_TYPE_PROJECT_INFO = "project_info"
RESPONSE_TYPE_LORE_STATUS = "lore_status"

# =============================================================================
# Icon/Emoji Constants
# =============================================================================
ICON_FILE = "📄"
ICON_FOLDER = "📁"
ICON_SUCCESS = "✓"
ICON_WARNING = "⚠"
ICON_ERROR = "❌"

# =============================================================================
# Message Templates
# =============================================================================
MSG_NO_PROJECT_MOUNTED = "No Godot project is currently mounted."
MSG_NO_FILE_CONTEXT = "No file context to clear."
MSG_NO_LORE_DIRECTORY = "Lore directory not found"
MSG_NO_LORE_FILES = "No lore files found"
MSG_CREATE_LORE_DIRECTORY = "Create the directory and add .txt, .md, or .rst files"
MSG_ADD_LORE_FILES = "Add .txt, .md, or .rst files to the lore directory"
MSG_PROJECT_DETECTED = "Valid Godot project detected (project.godot found)"
MSG_NO_PROJECT_FILE = "No project.godot found - may not be a Godot project root"
MSG_FILE_LOADED = "File loaded into context! You can now ask questions about this file."
MSG_USE_CLEAR = "Use /clear to remove file context."
MSG_THINKING = "Thinking..."
MSG_LOADING_DB = "Loading existing vector database..."
MSG_CREATING_DB = "Creating new vector database from Godot documentation and lore..."
MSG_NO_DOCUMENTS = "No documents found! The assistant will have limited capabilities."
MSG_GOODBYE = "Goodbye!"

# =============================================================================
# Error Messages
# =============================================================================
ERROR_NO_VECTORSTORE = (
    "Vectorstore not initialized. Call load_or_create_vectorstore first."
)
ERROR_NO_QA_CHAIN = "QA chain not initialized. Call setup_qa_chain first."
ERROR_FILE_NOT_FOUND = "File not found: {file_path}"
ERROR_NO_FILES_MATCHING = "No files found matching: {pattern}"
ERROR_READ_COMMAND_USAGE = "/read requires a file path. Usage: /read <file>"
ERROR_UNKNOWN_COMMAND = "Unknown command: {command}"
ERROR_INVALID_API_PROVIDER = (
    "Invalid API_PROVIDER: {provider}. Must be 'anthropic' or 'openai'"
)
ERROR_INVALID_EMBEDDING_PROVIDER = (
    "Invalid EMBEDDING_PROVIDER: {provider}. Must be 'local' or 'openai'"
)
ERROR_MISSING_API_KEY = "{key_name} not found in environment"
ERROR_OPENAI_KEY_REQUIRED = "OPENAI_API_KEY required for OpenAI embeddings"
ERROR_DEPENDENCY_NOT_REGISTERED = "Dependency '{name}' not registered in container"
ERROR_PROJECT_ANALYZER_REQUIRED = "project_analyzer is required in CommandContext"

# =============================================================================
# Success Messages
# =============================================================================
SUCCESS_DB_CREATED = "Vector database created successfully!"
SUCCESS_CLEARED_CONTEXT = "Cleared file context for: {file_path}"
SUCCESS_ASSISTANT_INITIALIZED = "Assistant initialized successfully"
SUCCESS_CONFIG_LOADED = "Configuration loaded successfully!"

# =============================================================================
# Info Messages
# =============================================================================
INFO_USING_LOCAL_EMBEDDINGS = "Using local embeddings (free, no API key needed)"
INFO_USING_OPENAI_EMBEDDINGS = "Using OpenAI embeddings"
INFO_LOADING_GODOT_DOCS = "Loading Godot documentation..."
INFO_LOADING_LORE = "Loading lore documents from {path}..."
INFO_SPLITTING_DOCUMENTS = "Splitting documents into chunks..."
INFO_CREATING_EMBEDDINGS = "Creating embeddings and storing in vector database..."
INFO_TOTAL_LORE_LOADED = "Total lore documents loaded: {count}"
INFO_LOADED_DOCS = "Loaded {count} documentation files"
INFO_LOADED_LORE_PATTERN = "Loaded {count} {pattern} files"
INFO_CREATED_CHUNKS = "Created {count} chunks"
INFO_LOADED_DOCUMENTS = "Loaded {count} documents"
INFO_TOTAL_TO_PROCESS = "Total documents to process: {count}"
INFO_SOURCES_RETRIEVED = "Sources: {count} relevant chunks retrieved"
INFO_SOURCES_FROM_DOCS = "{count} from documentation"
INFO_SOURCES_FROM_LORE = "{count} from lore"
INFO_CONTEXT_FILE = "Context: {file_path}"

# =============================================================================
# Truncation Messages
# =============================================================================
TRUNCATE_MSG_FILES = "... and {count} more"
TRUNCATE_MSG_CONTENT = "... (showing first {shown} chars of {total} total)"

# =============================================================================
# Autodetect Encoding
# =============================================================================
LOADER_AUTODETECT_ENCODING = True

# =============================================================================
# File Size Display
# =============================================================================
FILE_SIZE_FORMAT = "{size:,} bytes"

# =============================================================================
# Project Structure Display
# =============================================================================
INDENT_SPACES = 2
INDENT_CHAR = " "

# =============================================================================
# HTML/Web Constants
# =============================================================================
HTML_PRE_TAG_OPEN = "<pre>"
HTML_PRE_TAG_CLOSE = "</pre>"

# =============================================================================
# Pytest Configuration
# =============================================================================
PYTEST_VERBOSITY = "-v"
TEST_API_KEY = "test_key"
TEST_MODEL_RESPONSE = "Test response"

# =============================================================================
# Docker/Container Configuration
# =============================================================================
DOCKER_WORKDIR = "/app"

# =============================================================================
# Test Constants
# =============================================================================
TEST_FILE_CONTENT = "Test file content"
TEST_PROJECT_INFO = "Test project info"
TEST_STRUCTURE = "Test structure"
TEST_ANSWER = "Test answer"
