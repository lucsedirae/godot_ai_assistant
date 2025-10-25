# src/commands/parser.py
"""
Command parser for converting user input into Command objects.
"""
from typing import Optional
from .base import Command, InvalidCommandError
from .project_commands import (
    ProjectInfoCommand,
    ProjectStructureCommand,
    ListFilesCommand,
    ReadFileCommand,
    ClearContextCommand,
    LoreStatusCommand,
    HelpCommand,
)
from constants import (
    COMMAND_PREFIX,
    COMMAND_PROJECT,
    COMMAND_READ,
    COMMAND_LIST,
    COMMAND_LORE,
    COMMAND_CLEAR,
)


class CommandParser:
    """
    Parses user input and returns appropriate Command objects.
    """

    def parse(self, input_text: str) -> Optional[Command]:
        """
        Parse user input and return a Command object if it's a valid command.

        Args:
                input_text: Raw user input string

        Returns:
                Command object if input is a valid command, None if it's a regular query

        Raises:
                InvalidCommandError: If command syntax is invalid
        """
        text = input_text.strip()

        # Not a command - return None to indicate regular query
        if not text.startswith(COMMAND_PREFIX):
            return None

        # Parse /project commands
        if text.startswith(COMMAND_PROJECT):
            return self._parse_project_command(text)

        # Parse /read command
        if text.startswith(COMMAND_READ):
            return self._parse_read_command(text)

        # Parse /list command
        if text.startswith(COMMAND_LIST):
            return self._parse_list_command(text)

        # Parse /lore command
        if text.startswith(COMMAND_LORE):
            return LoreStatusCommand()

        # Parse /clear command
        if text.startswith(COMMAND_CLEAR):
            return ClearContextCommand()

        # Unknown command
        raise InvalidCommandError(f"Unknown command: {text.split()[0]}")

    def _parse_project_command(self, text: str) -> Command:
        """
        Parse /project subcommands.

        Args:
                text: Command text starting with /project

        Returns:
                Appropriate project command

        Raises:
                InvalidCommandError: If subcommand is invalid
        """
        text_lower = text.lower()

        if "info" in text_lower:
            return ProjectInfoCommand()
        elif "structure" in text_lower:
            return ProjectStructureCommand()
        else:
            return HelpCommand()

    def _parse_read_command(self, text: str) -> Command:
        """
        Parse /read command.

        Args:
                text: Command text starting with /read

        Returns:
                ReadFileCommand with the specified file path

        Raises:
                InvalidCommandError: If no file path provided
        """
        parts = text.split(maxsplit=1)

        if len(parts) < 2 or not parts[1].strip():
            raise InvalidCommandError("/read requires a file path. Usage: /read <file>")

        file_path = parts[1].strip()
        return ReadFileCommand(file_path)

    def _parse_list_command(self, text: str) -> Command:
        """
        Parse /list command.

        Args:
                text: Command text starting with /list

        Returns:
                ListFilesCommand with the specified pattern (or default)
        """
        parts = text.split(maxsplit=1)

        if len(parts) < 2 or not parts[1].strip():
            # Use default pattern
            return ListFilesCommand()

        pattern = parts[1].strip()
        return ListFilesCommand(pattern)

    def is_command(self, input_text: str) -> bool:
        """
        Check if input text is a command (starts with /).

        Args:
                input_text: User input string

        Returns:
                True if input is a command, False otherwise
        """
        return input_text.strip().startswith("/")


# Convenience function for quick parsing
def parse_command(input_text: str) -> Optional[Command]:
    """
    Parse user input and return a Command object.

    Args:
            input_text: Raw user input string

    Returns:
            Command object if input is a valid command, None if it's a regular query

    Raises:
            InvalidCommandError: If command syntax is invalid
    """
    parser = CommandParser()
    return parser.parse(input_text)
