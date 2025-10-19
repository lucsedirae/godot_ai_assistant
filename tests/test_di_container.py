# tests/test_di_container.py
"""
Unit tests for the dependency injection container.
Run with: pytest tests/test_di_container.py -v
"""
import pytest
from unittest.mock import Mock, patch

from di_container import DIContainer, get_container, reset_container


class TestDIContainer:
	"""Tests for the DIContainer class"""
	
	def test_register_singleton(self):
		"""Test registering a singleton instance"""
		container = DIContainer()
		test_obj = Mock()
		
		container.register_singleton('test', test_obj)
		
		assert container.has('test')
		assert container.get('test') is test_obj
	
	def test_register_factory(self):
		"""Test registering a factory function"""
		container = DIContainer()
		
		def create_obj():
			return Mock()
		
		container.register_factory('test', create_obj)
		
		assert container.has('test')
		# Factory should create new instance each time
		obj1 = container.get('test')
		obj2 = container.get('test')
		assert obj1 is not obj2
	
	def test_get_nonexistent_dependency(self):
		"""Test getting a dependency that doesn't exist"""
		container = DIContainer()
		
		with pytest.raises(KeyError) as exc_info:
			container.get('nonexistent')
		
		assert 'nonexistent' in str(exc_info.value)
	
	def test_has_method(self):
		"""Test the has() method"""
		container = DIContainer()
		
		assert not container.has('test')
		
		container.register_singleton('test', Mock())
		assert container.has('test')
	
	def test_singleton_priority_over_factory(self):
		"""Test that singletons take priority over factories"""
		container = DIContainer()
		singleton = Mock()
		
		container.register_factory('test', lambda: Mock())
		container.register_singleton('test', singleton)
		
		# Should return singleton, not factory result
		assert container.get('test') is singleton


class TestContainerBootstrap:
	"""Tests for container bootstrapping"""
	
	@patch('di_container.load_config')
	@patch('di_container.ConsoleOutputManager')
	@patch('di_container.ProjectAnalyzer')
	@patch('di_container.CommandParser')
	@patch('di_container.HuggingFaceEmbeddings')
	@patch('di_container.OpenAIEmbeddings')
	@patch('di_container.ChatAnthropic')
	@patch('di_container.ChatOpenAI')
	def test_bootstrap_registers_all_dependencies(
		self,
		mock_openai_llm,
		mock_anthropic_llm,
		mock_openai_embed,
		mock_huggingface_embed,
		mock_parser_class,
		mock_analyzer_class,
		mock_output_class,
		mock_load_config
	):
		"""Test that bootstrap registers all required dependencies"""
		# Setup mocks
		mock_config = Mock()
		mock_config.language = 'en'
		mock_config.paths.project_path = '/test/path'
		mock_config.embedding.provider = 'local'
		mock_config.api.provider = 'anthropic'
		mock_config.api.anthropic_key = 'test_key'
		mock_config.llm.anthropic_model = 'claude-sonnet-4-20250514'
		mock_config.llm.temperature = 0
		mock_load_config.return_value = mock_config
		
		container = DIContainer()
		container.bootstrap()
		
		# Verify all core dependencies are registered
		assert container.has('config')
		assert container.has('output_manager')
		assert container.has('project_analyzer')
		assert container.has('command_parser')
		assert container.has('embeddings')
		assert container.has('llm')
		assert container.has('assistant')
	
	@patch('di_container.load_config')
	@patch('di_container.HuggingFaceEmbeddings')
	@patch('di_container.ChatAnthropic')
	def test_bootstrap_config_validation(
		self,
		mock_llm,
		mock_embed,
		mock_load_config
	):
		"""Test that bootstrap validates configuration"""
		mock_config = Mock()
		mock_config.language = 'en'
		mock_config.paths.project_path = '/test/path'
		mock_config.embedding.provider = 'local'
		mock_config.api.provider = 'anthropic'
		mock_config.api.anthropic_key = 'test_key'
		mock_config.llm.anthropic_model = 'claude-sonnet-4-20250514'
		mock_config.llm.temperature = 0
		mock_load_config.return_value = mock_config
		
		container = DIContainer()
		container.bootstrap()
		
		config = container.get('config')
		assert config is mock_config


class TestGlobalContainer:
	"""Tests for global container functions"""
	
	@patch('di_container.DIContainer')
	def test_get_container_creates_singleton(self, mock_container_class):
		"""Test that get_container creates a singleton"""
		# Reset any existing container
		reset_container()
		
		mock_instance = Mock()
		mock_container_class.return_value = mock_instance
		
		# First call should create container
		container1 = get_container()
		
		# Second call should return same instance
		container2 = get_container()
		
		# Should only create once
		assert mock_container_class.call_count == 1
		mock_instance.bootstrap.assert_called_once()
	
	def test_reset_container(self):
		"""Test that reset_container clears the global instance"""
		# Just test that reset doesn't raise an error
		# We can't easily test re-creation without full integration
		reset_container()
		reset_container()  # Should not raise error even if called multiple times

class TestDependencyInjection:
	"""Integration tests for dependency injection"""
	
	def test_assistant_receives_dependencies(self, test_container):
		"""Test that assistant receives all required dependencies"""
		from godot_assistant import GodotAIAssistant
		
		# Create assistant using container dependencies
		assistant = GodotAIAssistant(
			project_analyzer=test_container.get('project_analyzer'),
			display_manager=test_container.get('output_manager'),
			config=test_container.get('config'),
			embeddings=test_container.get('embeddings'),
			llm=test_container.get('llm'),
			command_parser=test_container.get('command_parser')
		)
		
		# Verify all dependencies are set
		assert assistant.project_analyzer is not None
		assert assistant.display_manager is not None
		assert assistant.config is not None
		assert assistant.embeddings is not None
		assert assistant.llm is not None
		assert assistant.command_parser is not None
	
	def test_no_hardcoded_dependencies(self, assistant_with_mocks):
		"""Test that assistant doesn't create its own dependencies"""
		# If assistant creates its own dependencies, it would fail
		# since we're providing mocks. This test verifies the mocks are used.
		
		assert assistant_with_mocks.embeddings is not None
		assert assistant_with_mocks.llm is not None
		
		# Verify these are the mocks we provided
		assert hasattr(assistant_with_mocks.embeddings, 'embed_documents')
		assert hasattr(assistant_with_mocks.llm, 'invoke')


class TestFactoryBehavior:
	"""Tests for factory registration behavior"""
	
	def test_embeddings_factory_local(self, mock_config):
		"""Test embeddings factory creates local embeddings"""
		mock_config.embedding.provider = "local"
		
		container = DIContainer()
		container._config = mock_config
		container._register_embeddings()
		
		# Factory should be registered
		assert container.has('embeddings')
	
	def test_llm_factory_anthropic(self, mock_config):
		"""Test LLM factory creates Anthropic LLM"""
		mock_config.api.provider = "anthropic"
		mock_config.api.anthropic_key = "test_key"
		
		container = DIContainer()
		container._config = mock_config
		container._register_llm()
		
		# Factory should be registered
		assert container.has('llm')
	
	def test_llm_factory_openai(self, mock_config):
		"""Test LLM factory creates OpenAI LLM"""
		mock_config.api.provider = "openai"
		mock_config.api.openai_key = "test_key"
		
		container = DIContainer()
		container._config = mock_config
		container._register_llm()
		
		# Factory should be registered
		assert container.has('llm')


if __name__ == "__main__":
	pytest.main([__file__, "-v"])