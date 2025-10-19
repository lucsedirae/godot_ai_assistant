# Dependency Injection Architecture (Add to README.md)

## Architecture Overview

The Godot AI Development Assistant uses **dependency injection** for improved testability, maintainability, and flexibility.

### Key Benefits

- 🧪 **Testable**: All dependencies can be mocked for unit testing
- 🔧 **Maintainable**: Clear dependency relationships
- 🔄 **Flexible**: Easy to swap implementations (e.g., different LLMs)
- 📦 **Modular**: Components are loosely coupled

### Dependency Injection Container

The `DIContainer` manages all application dependencies:

```python
from di_container import get_container

# Get the global container
container = get_container()

# Retrieve dependencies
config = container.get('config')
assistant = container.get('assistant')
```

### Available Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `config` | Singleton | Application configuration |
| `output_manager` | Singleton | Console output manager |
| `project_analyzer` | Singleton | Project file analyzer |
| `command_parser` | Singleton | Command parser |
| `embeddings` | Factory | Embedding model (OpenAI or local) |
| `llm` | Factory | Language model (Anthropic or OpenAI) |
| `vectorstore` | Factory | ChromaDB vector store |
| `assistant` | Singleton | Main Godot AI assistant |

### For Developers

#### Using Dependencies in Your Code

```python
from di_container import get_container

def my_function():
	container = get_container()
	assistant = container.get('assistant')
	config = container.get('config')
	
	# Use dependencies
	print(f"Using {config.api.provider} API")
	assistant.ask("What is a Node2D?")
```

#### Creating Custom Services

```python
class MyService:
	def __init__(self, project_analyzer, config):
		"""Dependencies are injected via constructor"""
		self.project_analyzer = project_analyzer
		self.config = config
	
	def analyze(self):
		files = self.project_analyzer.find_files("*.gd")
		return f"Found {len(files)} GDScript files"

# Use in your code
container = get_container()
service = MyService(
	project_analyzer=container.get('project_analyzer'),
	config=container.get('config')
)
result = service.analyze()
```

#### Testing with Mocks

```python
from unittest.mock import Mock

def test_my_service():
	# Create mock dependencies
	mock_analyzer = Mock()
	mock_analyzer.find_files.return_value = ["file1.gd", "file2.gd"]
	
	mock_config = Mock()
	
	# Inject mocks
	service = MyService(mock_analyzer, mock_config)
	result = service.analyze()
	
	# Verify
	assert "Found 2 GDScript files" in result
	mock_analyzer.find_files.assert_called_once()
```

### Documentation

For detailed information about the DI system:

- **[Migration Guide](DEPENDENCY_INJECTION_MIGRATION.md)** - Comprehensive guide to the DI refactoring
- **[Quick Reference](DI_QUICK_REFERENCE.md)** - Quick reference for common patterns
- **[Usage Examples](examples/di_usage_example.py)** - Practical code examples

### Running Tests

The project uses pytest with DI-aware fixtures:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_di_container.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Common Test Fixtures

```python
# Available in all tests (from conftest.py)
def test_with_assistant(assistant_with_mocks):
	"""All dependencies are mocked"""
	result = assistant_with_mocks.ask("test")
	assert result is not None

def test_with_container(test_container):
	"""Container with mocked dependencies"""
	config = test_container.get('config')
	assert config is not None

def test_custom(mock_config, mock_llm):
	"""Individual mocked dependencies"""
	assert mock_config.api.provider == "anthropic"
```

### Extending the System

To add new dependencies:

1. Create your service class with constructor injection
2. Register in `di_container.py`:

```python
def _register_my_service(self):
	service = MyService(
		dependency1=self.get('dependency1'),
		dependency2=self.get('dependency2')
	)
	self.register_singleton('my_service', service)

def bootstrap(self):
	# ... existing code ...
	self._register_my_service()
```

3. Use anywhere:

```python
container = get_container()
my_service = container.get('my_service')
```

### Troubleshooting

**Error: `KeyError: 'dependency'`**
- Ensure the dependency is registered in `di_container.bootstrap()`

**Tests failing with real API calls**
- Use test fixtures: `assistant_with_mocks`, `test_container`
- See `tests/conftest.py` for available fixtures

**Container not resetting between tests**
- The `cleanup_container` fixture automatically handles this
- For manual reset: `reset_container()`

### Performance

- **Container bootstrapping**: ~1-2 seconds on first call (loads config, creates embeddings)
- **Subsequent calls**: Instant (returns cached instance)
- **Memory**: Singletons persist for application lifetime, factories create new instances

### Architecture Diagram

```
┌─────────────────────────────────────────┐
│          DIContainer                     │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐      │
│  │  Singletons │  │  Factories  │      │
│  ├─────────────┤  ├─────────────┤      │
│  │ • config    │  │ • embeddings│      │
│  │ • assistant │  │ • llm       │      │
│  │ • analyzer  │  │ • vectorstore│     │
│  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────┘
           │
           │ injects
           ▼
┌─────────────────────────────────────────┐
│      GodotAIAssistant                   │
├─────────────────────────────────────────┤
│  • project_analyzer (injected)          │
│  • display_manager (injected)           │
│  • config (injected)                    │
│  • embeddings (injected)                │
│  • llm (injected)                       │
│  • command_parser (injected)            │
└─────────────────────────────────────────┘
```

### Best Practices

✅ **Do:**
- Inject dependencies through constructors
- Use test fixtures for mocking
- Register new dependencies in `bootstrap()`
- Document dependencies in docstrings

❌ **Don't:**
- Create dependencies inside classes
- Use global variables
- Import container in every module (use constructor injection)
- Forget to reset container in tests

---

**Note**: This architecture change is backward compatible. All existing functionality works exactly as before, with no changes required for end users.