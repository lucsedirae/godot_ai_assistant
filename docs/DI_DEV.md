# Dependency Injection Quick Reference

## Quick Start

### Get the Container
```python
from di_container import get_container

container = get_container()
```

### Get a Dependency
```python
config = container.get('config')
assistant = container.get('assistant')
llm = container.get('llm')
```

### Available Dependencies
```python
'config'           # AppConfig instance
'output_manager'   # ConsoleOutputManager
'project_analyzer' # ProjectAnalyzer
'command_parser'   # CommandParser
'embeddings'       # Embeddings (OpenAI or local)
'llm'              # LLM (Anthropic or OpenAI)
'vectorstore'      # ChromaDB vector store
'assistant'        # GodotAIAssistant
```

## Testing

### Use Pre-configured Fixtures
```python
def test_with_mocked_assistant(assistant_with_mocks):
	"""All dependencies are mocked"""
	result = assistant_with_mocks.ask("test")

def test_with_container(test_container):
	"""Container with mocked dependencies"""
	config = test_container.get('config')

def test_with_mock_config(mock_config):
	"""Just the config"""
	assert mock_config.api.provider == "anthropic"
```

### Create Custom Mocks
```python
from unittest.mock import Mock

def test_custom():
	mock_llm = Mock()
	mock_llm.invoke = Mock(return_value="test response")
	
	assistant = GodotAIAssistant(
		...,
		llm=mock_llm
	)
```

## Registering New Dependencies

### Register a Singleton
```python
# In di_container.py
def _register_my_service(self):
	service = MyService(self.get('dependency'))
	self.register_singleton('my_service', service)

# In bootstrap()
def bootstrap(self):
	# ... existing code ...
	self._register_my_service()
```

### Register a Factory
```python
def _register_my_factory(self):
	def create():
		return MyObject()
	self.register_factory('my_object', create)
```

## Common Patterns

### Pattern: Inject Dependencies in Constructor
```python
class MyClass:
	def __init__(self, dependency1, dependency2):
		self.dep1 = dependency1
		self.dep2 = dependency2
```

### Pattern: Get Container in Function
```python
def my_function():
	container = get_container()
	config = container.get('config')
	# Use config
```

### Pattern: Reset Container (Testing)
```python
from di_container import reset_container

def test_something():
	reset_container()
	# Fresh container
```

## Checklist for New Components

When creating a new component:

1. ✅ Accept dependencies in `__init__`
2. ✅ Don't create dependencies inside the class
3. ✅ Register in `di_container.bootstrap()`
4. ✅ Add test fixtures in `conftest.py`
5. ✅ Document dependencies in docstring

## Example: Adding a New Service

```python
# 1. Create the service
class MyService:
	def __init__(self, config, llm):
		self.config = config
		self.llm = llm
	
	def do_something(self):
		# Implementation

# 2. Register in di_container.py
def _register_my_service(self):
	service = MyService(
		config=self.get('config'),
		llm=self.get('llm')
	)
	self.register_singleton('my_service', service)

def bootstrap(self):
	# ... existing registrations ...
	self._register_my_service()

# 3. Use anywhere
container = get_container()
my_service = container.get('my_service')
my_service.do_something()

# 4. Test it
def test_my_service(mock_config, mock_llm):
	service = MyService(mock_config, mock_llm)
	result = service.do_something()
	assert result is not None
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `KeyError: 'dependency'` | Register in `bootstrap()` |
| Tests fail with real API | Use `assistant_with_mocks` fixture |
| Container not resetting | Use `cleanup_container` fixture |
| Circular dependency | Refactor or use factory pattern |
| Import error | Check `sys.path` in `conftest.py` |

## When to Use Singleton vs Factory

### Use Singleton For:
- Configuration (loaded once)
- Database connections
- Expensive-to-create objects
- Stateful services

### Use Factory For:
- Stateless objects
- Per-request instances
- Lightweight objects
- When you need fresh instances

## Code Smells to Avoid

❌ **Don't create dependencies inside classes**
```python
class Bad:
	def __init__(self):
		self.llm = ChatAnthropic(...)  # Creates own dependency
```

✅ **Do inject dependencies**
```python
class Good:
	def __init__(self, llm):
		self.llm = llm  # Dependency injected
```

❌ **Don't use global variables**
```python
llm = ChatAnthropic(...)  # Global

class Bad:
	def use_llm(self):
		return llm.invoke(...)
```

✅ **Do use the container**
```python
class Good:
	def __init__(self, llm):
		self.llm = llm
	
	def use_llm(self):
		return self.llm.invoke(...)
```

## Benefits Recap

- 🧪 **Testable**: Easy to mock dependencies
- 🔧 **Maintainable**: Clear dependency graph
- 🔄 **Flexible**: Swap implementations easily
- 📦 **Decoupled**: Components independent
- 📝 **Explicit**: All dependencies visible

## Related Documentation

- Full guide: `DEPENDENCY_INJECTION_MIGRATION.md`
- Tests: `tests/test_di_container.py`
- Implementation: `src/di_container.py`