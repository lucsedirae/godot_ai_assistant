# src/commands/project_commands.py
from .base import Command, CommandContext
from constants import (
    MAX_FILES_IN_LIST,
    MAX_FILE_CONTENT_DISPLAY,
)


class ProjectInfoCommand(Command):
    """Display project information"""

    def execute(self, context: CommandContext) -> str:
        """
        Get basic project information.

        Args:
                context: Command execution context

        Returns:
                Formatted project information string
        """
        info = context.project_analyzer.get_project_info()
        return f"<pre>{info}</pre>"


class ProjectStructureCommand(Command):
    """Display project file structure"""

    def execute(self, context: CommandContext) -> str:
        """
        Get project file structure tree.

        Args:
                context: Command execution context

        Returns:
                Formatted project structure string
        """
        structure = context.project_analyzer.get_project_structure()
        return f"<pre>{structure}</pre>"


class ListFilesCommand(Command):
    """List files matching a pattern"""

    def __init__(self, pattern: str = "*.gd"):
        """
        Initialize the list files command.

        Args:
                pattern: File pattern to match (e.g., "*.gd", "*.tscn")
        """
        self.pattern = pattern

    def execute(self, context: CommandContext) -> str:
        """
        List files matching the specified pattern.

        Args:
                context: Command execution context

        Returns:
                Formatted file list string

        Raises:
                ValueError: If no files found matching pattern
        """
        files = context.project_analyzer.find_files(self.pattern)

        if not files:
            raise ValueError(f"No files found matching: {self.pattern}")

        file_list = "\n".join([f"  {f}" for f in files[:MAX_FILES_IN_LIST]])
        if len(files) > 50:
            file_list += f"\n\n... and {len(files) - 50} more"

        return f"<pre>📁 Files matching '{self.pattern}':\n{'='*80}\n{file_list}\n{'='*80}</pre>"


class ReadFileCommand(Command):
    """Read and display a project file"""

    def __init__(self, file_path: str):
        """
        Initialize the read file command.

        Args:
                file_path: Relative path to the file to read
        """
        self.file_path = file_path

    def execute(self, context: CommandContext) -> str:
        """
        Read and return file contents.

        Args:
                context: Command execution context

        Returns:
                Formatted file contents string

        Raises:
                FileNotFoundError: If file doesn't exist
        """
        from .base import FileNotFoundError as CmdFileNotFoundError

        content = context.project_analyzer.read_file(self.file_path)

        if content is None:
            raise CmdFileNotFoundError(f"File not found: {self.file_path}")

        # Store file in assistant's context if available
        if context.assistant:
            context.assistant.last_read_file = {
                "path": self.file_path,
                "content": content,
            }

        # Limit display for web/console
        display_content = content[:MAX_FILE_CONTENT_DISPLAY]
        if len(content) > MAX_FILE_CONTENT_DISPLAY:
            display_content += (
                f"\n\n... (showing first 3000 chars of {len(content)} total)"
            )

        result = f"""<pre>📄 Contents of {self.file_path}:
{'='*80}
{display_content}
{'='*80}

✓ File loaded into context! You can now ask questions about this file.
Use /clear to remove file context.</pre>"""

        return result


class ClearContextCommand(Command):
    """Clear the loaded file context"""

    def execute(self, context: CommandContext) -> str:
        """
        Clear the last read file from context.

        Args:
                context: Command execution context

        Returns:
                Success message or info if nothing to clear
        """
        if context.assistant and context.assistant.last_read_file:
            file_path = context.assistant.last_read_file["path"]
            context.assistant.last_read_file = None
            return f"✓ Cleared file context for: {file_path}"
        else:
            return "No file context to clear."


class LoreStatusCommand(Command):
    """Show lore files status"""

    def execute(self, context: CommandContext) -> str:
        """
        Display status of lore files.

        Args:
                context: Command execution context

        Returns:
                Formatted lore status string
        """
        if not context.assistant:
            return "Assistant not available"

        lore_path = context.assistant.config.paths.lore_path
        result = ["Lore Status:", "=" * 80]

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

        result.append("=" * 80)

        return f"<pre>{chr(10).join(result)}</pre>"


class HelpCommand(Command):
    """Display available commands"""

    def execute(self, context: CommandContext) -> str:
        """
        Display help information about available commands.

        Args:
                context: Command execution context

        Returns:
                Formatted help text
        """
        help_text = """Available Commands:
- /project info      - Show project information
- /project structure - Show project file structure
- /read <file>       - Read a specific file (loads into context)
- /list [pattern]    - List files (default: *.gd)
- /lore              - Show lore files status
- /clear             - Clear loaded file context"""

        return f"<pre>{help_text}</pre>"
