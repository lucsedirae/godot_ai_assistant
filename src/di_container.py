# src/di_container.py
"""
Dependency Injection Container for Godot AI Development Assistant.

This module provides a centralized DI container that manages all application
dependencies and their lifecycles.
"""
from typing import Dict, Any, Callable, Optional
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from config import AppConfig, load_config
from project_analyzer import ProjectAnalyzer
from console_output import ConsoleOutputManager
from commands import CommandParser


class DIContainer:
	"""
	Dependency Injection Container that manages application dependencies.
	
	Supports singleton and factory patterns for different dependency lifecycles.
	"""
	
	def __init__(self):
		"""Initialize the DI container with empty registries."""
		self._singletons: Dict[str, Any] = {}
		self._factories: Dict[str, Callable] = {}
		self._config: Optional[AppConfig] = None
	
	def register_singleton(self, name: str, instance: Any) -> None:
		"""
		Register a singleton instance.
		
		Args:
			name: Identifier for the dependency
			instance: The singleton instance to register
		"""
		self._singletons[name] = instance
	
	def register_factory(self, name: str, factory: Callable) -> None:
		"""
		Register a factory function for creating instances.
		
		Args:
			name: Identifier for the dependency
			factory: Callable that creates the dependency
		"""
		self._factories[name] = factory
	
	def get(self, name: str) -> Any:
		"""
		Resolve a dependency by name.
		
		Args:
			name: Identifier for the dependency
			
		Returns:
			The resolved dependency instance
			
		Raises:
			KeyError: If dependency not found
		"""
		# Check singletons first
		if name in self._singletons:
			return self._singletons[name]
		
		# Check factories
		if name in self._factories:
			return self._factories[name]()
		
		raise KeyError(f"Dependency '{name}' not registered in container")
	
	def has(self, name: str) -> bool:
		"""
		Check if a dependency is registered.
		
		Args:
			name: Identifier for the dependency
			
		Returns:
			True if dependency exists, False otherwise
		"""
		return name in self._singletons or name in self._factories
	
	def bootstrap(self) -> None:
		"""
		Bootstrap the application by registering all dependencies.
		
		This is the main initialization method that sets up all services.
		"""
		# Load and register configuration
		self._config = load_config()
		self.register_singleton('config', self._config)
		
		# Register core services
		self._register_output_manager()
		self._register_project_analyzer()
		self._register_command_parser()
		
		# Register AI/ML components
		self._register_embeddings()
		self._register_llm()
		self._register_vectorstore()
		
		# Register assistant (depends on above components)
		self._register_assistant()
	
	def _register_output_manager(self) -> None:
		"""Register the console output manager."""
		output_manager = ConsoleOutputManager(self._config.language)
		self.register_singleton('output_manager', output_manager)
	
	def _register_project_analyzer(self) -> None:
		"""Register the project analyzer."""
		project_analyzer = ProjectAnalyzer(self._config.paths.project_path)
		self.register_singleton('project_analyzer', project_analyzer)
	
	def _register_command_parser(self) -> None:
		"""Register the command parser."""
		command_parser = CommandParser()
		self.register_singleton('command_parser', command_parser)
	
	def _register_embeddings(self) -> None:
		"""Register embeddings based on configuration."""
		def create_embeddings():
			if self._config.embedding.provider == "local":
				return HuggingFaceEmbeddings(
					model_name="all-MiniLM-L6-v2",
					model_kwargs={'device': 'cpu'}
				)
			else:
				return OpenAIEmbeddings(
					openai_api_key=self._config.api.openai_key
				)
		
		# Use factory since embeddings might be recreated
		self.register_factory('embeddings', create_embeddings)
	
	def _register_llm(self) -> None:
		"""Register LLM based on configuration."""
		def create_llm():
			if self._config.api.provider == "anthropic":
				return ChatAnthropic(
					model=self._config.llm.anthropic_model,
					temperature=self._config.llm.temperature,
					anthropic_api_key=self._config.api.anthropic_key
				)
			else:
				return ChatOpenAI(
					model=self._config.llm.openai_model,
					temperature=self._config.llm.temperature,
					openai_api_key=self._config.api.openai_key
				)
		
		self.register_factory('llm', create_llm)
	
	def _register_vectorstore(self) -> None:
		"""Register vector store."""
		def create_vectorstore():
			embeddings = self.get('embeddings')
			db_path = self._config.paths.db_path
			
			if db_path.exists() and list(db_path.iterdir()):
				return Chroma(
					persist_directory=str(db_path),
					embedding_function=embeddings
				)
			return None
		
		# Vectorstore is created lazily and cached
		self.register_factory('vectorstore', create_vectorstore)
	
	def _register_assistant(self) -> None:
		"""Register the main Godot AI Assistant."""
		# Import here to avoid circular dependency
		from godot_assistant import GodotAIAssistant
		
		def create_assistant():
			return GodotAIAssistant(
				project_analyzer=self.get('project_analyzer'),
				display_manager=self.get('output_manager'),
				config=self.get('config'),
				embeddings=self.get('embeddings'),
				llm=self.get('llm'),
				command_parser=self.get('command_parser')
			)
		
		# Assistant is a singleton
		assistant = create_assistant()
		self.register_singleton('assistant', assistant)


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
	"""
	Get the global DI container instance.
	
	Creates and bootstraps the container on first call.
	
	Returns:
		The global DIContainer instance
	"""
	global _container
	if _container is None:
		_container = DIContainer()
		_container.bootstrap()
	return _container


def reset_container() -> None:
	"""
	Reset the global container.
	
	Useful for testing or reinitialization.
	"""
	global _container
	_container = None