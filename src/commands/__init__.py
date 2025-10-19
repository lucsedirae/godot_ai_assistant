# src/commands/__init__.py
"""
Command pattern implementation for Godot AI Assistant.

This package provides a clean separation between command parsing,
execution, and presentation logic.
"""

from .base import (
	Command,
	CommandContext,
	CommandError,
	FileNotFoundError,
	InvalidCommandError
)

from .project_commands import (
	ProjectInfoCommand,
	ProjectStructureCommand,
	ListFilesCommand,
	ReadFileCommand,
	ClearContextCommand,
	LoreStatusCommand,
	HelpCommand
)

from .parser import CommandParser, parse_command

__all__ = [
	# Base classes
	'Command',
	'CommandContext',
	'CommandError',
	'FileNotFoundError',
	'InvalidCommandError',
	
	# Commands
	'ProjectInfoCommand',
	'ProjectStructureCommand',
	'ListFilesCommand',
	'ReadFileCommand',
	'ClearContextCommand',
	'LoreStatusCommand',
	'HelpCommand',
	
	# Parser
	'CommandParser',
	'parse_command',
]