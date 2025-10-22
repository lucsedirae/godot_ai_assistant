# tests/conftest.py
"""
Pytest configuration and shared fixtures.
Enhanced with dependency injection fixtures for better testing.
"""
import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Now we can import our modules
from di_container import DIContainer, reset_container
from config import (
    AppConfig,
    APIConfig,
    EmbeddingConfig,
    PathConfig,
    RAGConfig,
    LLMConfig,
    WebConfig,
)


@pytest.fixture(scope="function")
def mock_config(tmp_path):
    """
    Create a mock configuration for testing.

    Args:
            tmp_path: Pytest fixture providing temporary directory

    Returns:
            Mock AppConfig instance
    """
    # Use tmp_path to avoid permission issues
    project_path = tmp_path / "project"
    project_path.mkdir()

    docs_path = tmp_path / "docs"
    docs_path.mkdir()

    lore_path = tmp_path / "lore"
    lore_path.mkdir()

    db_path = tmp_path / "db"
    db_path.mkdir()

    # Create a mock that doesn't validate paths
    mock = Mock()
    mock.api = Mock()
    mock.api.provider = "anthropic"
    mock.api.anthropic_key = "test_key"
    mock.api.openai_key = None

    mock.embedding = Mock()
    mock.embedding.provider = "local"

    mock.paths = Mock()
    mock.paths.project_path = project_path
    mock.paths.docs_path = docs_path
    mock.paths.lore_path = lore_path
    mock.paths.db_path = db_path

    mock.rag = Mock()
    mock.rag.chunk_size = 1000
    mock.rag.chunk_overlap = 200
    mock.rag.retrieval_k = 6

    mock.llm = Mock()
    mock.llm.anthropic_model = "claude-sonnet-4-20250514"
    mock.llm.openai_model = "gpt-4-turbo-preview"
    mock.llm.temperature = 0

    mock.web = Mock()
    mock.web.host = "0.0.0.0"
    mock.web.port = 5000
    mock.web.debug = True

    mock.language = "en"
    mock.get_model_name = Mock(return_value="claude-sonnet-4-20250514")

    return mock


@pytest.fixture(scope="function")
def mock_embeddings():
    """
    Create a mock embeddings instance.

    Returns:
            Mock embeddings object
    """
    mock = Mock()
    mock.embed_documents = Mock(return_value=[[0.1, 0.2, 0.3]])
    mock.embed_query = Mock(return_value=[0.1, 0.2, 0.3])
    return mock


@pytest.fixture(scope="function")
def mock_llm():
    """
    Create a mock LLM instance.

    Returns:
            Mock LLM object
    """
    mock = Mock()
    mock.invoke = Mock(return_value="Test response")
    return mock


@pytest.fixture(scope="function")
def mock_project_analyzer(tmp_path):
    """
    Create a mock ProjectAnalyzer instance.

    Args:
            tmp_path: Pytest fixture providing temporary directory

    Returns:
            Mock ProjectAnalyzer object
    """
    mock = Mock()
    mock.project_path = tmp_path / "project"
    mock.project_exists = True
    mock.get_project_info = Mock(return_value="Test project info")
    mock.get_project_structure = Mock(return_value="Test structure")
    mock.read_file = Mock(return_value="Test file content")
    mock.find_files = Mock(return_value=["file1.gd", "file2.gd"])
    return mock


@pytest.fixture(scope="function")
def mock_display_manager():
    """
    Create a mock ConsoleOutputManager instance.

    Returns:
            Mock ConsoleOutputManager object
    """
    mock = Mock()
    mock.get_string = Mock(return_value="Test prompt: ")
    mock.print_title = Mock()
    mock.print_welcome_message = Mock()
    mock.print_goodbye_message = Mock()
    mock.print_error = Mock()
    mock.print_project_status = Mock()
    return mock


@pytest.fixture(scope="function")
def mock_command_parser():
    """
    Create a mock CommandParser instance.

    Returns:
            Mock CommandParser object
    """
    from commands import CommandParser

    return CommandParser()


@pytest.fixture(scope="function")
def test_container(
    mock_config,
    mock_embeddings,
    mock_llm,
    mock_project_analyzer,
    mock_display_manager,
    mock_command_parser,
):
    """
    Create a test DI container with mocked dependencies.

    Args:
            mock_config: Mock configuration
            mock_embeddings: Mock embeddings
            mock_llm: Mock LLM
            mock_project_analyzer: Mock project analyzer
            mock_display_manager: Mock display manager
            mock_command_parser: Mock command parser

    Returns:
            DIContainer instance configured for testing
    """
    container = DIContainer()

    # Register all mocked dependencies
    container.register_singleton("config", mock_config)
    container.register_singleton("embeddings", mock_embeddings)
    container.register_singleton("llm", mock_llm)
    container.register_singleton("project_analyzer", mock_project_analyzer)
    container.register_singleton("output_manager", mock_display_manager)
    container.register_singleton("command_parser", mock_command_parser)

    return container


@pytest.fixture(scope="function")
def assistant_with_mocks(
    mock_config,
    mock_embeddings,
    mock_llm,
    mock_project_analyzer,
    mock_display_manager,
    mock_command_parser,
):
    """
    Create a GodotAIAssistant instance with all mocked dependencies.

    Args:
            mock_config: Mock configuration
            mock_embeddings: Mock embeddings
            mock_llm: Mock LLM
            mock_project_analyzer: Mock project analyzer
            mock_display_manager: Mock display manager
            mock_command_parser: Mock command parser

    Returns:
            GodotAIAssistant instance with mocked dependencies
    """
    from godot_assistant import GodotAIAssistant

    return GodotAIAssistant(
        project_analyzer=mock_project_analyzer,
        display_manager=mock_display_manager,
        config=mock_config,
        embeddings=mock_embeddings,
        llm=mock_llm,
        command_parser=mock_command_parser,
    )


@pytest.fixture(autouse=True)
def cleanup_container():
    """
    Automatically reset the DI container after each test.

    This ensures test isolation by preventing state leakage between tests.
    """
    yield
    reset_container()
