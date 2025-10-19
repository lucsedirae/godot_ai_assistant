# src/commands/base.py
"""
Base command interface and context for the command pattern.
"""
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass


@dataclass
class CommandContext:
	"""
	Context object passed to all commands containing necessary dependencies.
	"""
	project_analyzer: Any  # ProjectAnalyzer instance
	display_manager: Any  # ConsoleOutputManager instance
	assistant: Any  # GodotAIAssistant instance (may be None for some commands)
	
	def __post_init__(self):
		"""Validate that required dependencies are present"""
		if self.project_analyzer is None:
			raise ValueError("project_analyzer is required in CommandContext")


class Command(ABC):
	"""
	Abstract base class for all commands.
	
	All commands should inherit from this class and implement the execute method.
	"""
	
	@abstractmethod
	def execute(self, context: CommandContext) -> str:
		"""
		Execute the command with the given context.
		
		Args:
			context: CommandContext containing dependencies
			
		Returns:
			String result of the command execution
			
		Raises:
			Exception: If command execution fails
		"""
		pass
	
	def format_for_web(self, result: str, command_type: str = "success") -> dict:
		"""
		Format command result for web API response.
		
		Args:
			result: The command result string
			command_type: Type of response (success, error, info, etc.)
			
		Returns:
			Dictionary formatted for JSON response
		"""
		return {
			'answer': result,
			'type': command_type
		}


class CommandError(Exception):
	"""Base exception for command execution errors"""
	pass


class FileNotFoundError(CommandError):
	"""Raised when a requested file is not found"""
	pass


class InvalidCommandError(CommandError):
	"""Raised when command syntax is invalid"""
	pass