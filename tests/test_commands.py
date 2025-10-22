# tests/test_commands.py
"""
Unit tests for command pattern implementation.
Run with: pytest tests/test_commands.py -v
"""
import pytest
from unittest.mock import Mock
from pathlib import Path

# Import commands - conftest.py handles the path
from commands import (
    CommandContext,
    CommandParser,
    ProjectInfoCommand,
    ProjectStructureCommand,
    ReadFileCommand,
    ListFilesCommand,
    ClearContextCommand,
    LoreStatusCommand,
    HelpCommand,
    FileNotFoundError,
    InvalidCommandError,
)


# Fixtures
@pytest.fixture
def mock_context():
    """Create a mock CommandContext for testing"""
    mock_analyzer = Mock()
    mock_display = Mock()
    mock_assistant = Mock()
    mock_assistant.last_read_file = None
    mock_assistant.config = Mock()
    mock_assistant.config.paths = Mock()
    mock_assistant.config.paths.lore_path = Path("/app/data/lore")

    return CommandContext(
        project_analyzer=mock_analyzer,
        display_manager=mock_display,
        assistant=mock_assistant,
    )


@pytest.fixture
def parser():
    """Create a CommandParser instance"""
    return CommandParser()


# Parser Tests
class TestCommandParser:

    def test_parse_project_info(self, parser):
        cmd = parser.parse("/project info")
        assert isinstance(cmd, ProjectInfoCommand)

    def test_parse_project_structure(self, parser):
        cmd = parser.parse("/project structure")
        assert isinstance(cmd, ProjectStructureCommand)

    def test_parse_read_file(self, parser):
        cmd = parser.parse("/read test.gd")
        assert isinstance(cmd, ReadFileCommand)
        assert cmd.file_path == "test.gd"

    def test_parse_read_file_no_path(self, parser):
        with pytest.raises(InvalidCommandError):
            parser.parse("/read")

    def test_parse_list_default(self, parser):
        cmd = parser.parse("/list")
        assert isinstance(cmd, ListFilesCommand)
        assert cmd.pattern == "*.gd"

    def test_parse_list_custom_pattern(self, parser):
        cmd = parser.parse("/list *.tscn")
        assert isinstance(cmd, ListFilesCommand)
        assert cmd.pattern == "*.tscn"

    def test_parse_clear(self, parser):
        cmd = parser.parse("/clear")
        assert isinstance(cmd, ClearContextCommand)

    def test_parse_lore(self, parser):
        cmd = parser.parse("/lore")
        assert isinstance(cmd, LoreStatusCommand)

    def test_parse_help(self, parser):
        cmd = parser.parse("/project")
        assert isinstance(cmd, HelpCommand)

    def test_parse_not_command(self, parser):
        cmd = parser.parse("What is a Node2D?")
        assert cmd is None

    def test_parse_unknown_command(self, parser):
        with pytest.raises(InvalidCommandError):
            parser.parse("/unknown")

    def test_is_command(self, parser):
        assert parser.is_command("/project info") is True
        assert parser.is_command("regular question") is False


# Command Execution Tests
class TestProjectInfoCommand:

    def test_execute(self, mock_context):
        mock_context.project_analyzer.get_project_info.return_value = "Project Info"

        cmd = ProjectInfoCommand()
        result = cmd.execute(mock_context)

        assert "Project Info" in result
        assert "<pre>" in result
        mock_context.project_analyzer.get_project_info.assert_called_once()


class TestProjectStructureCommand:

    def test_execute(self, mock_context):
        mock_context.project_analyzer.get_project_structure.return_value = (
            "Project Structure"
        )

        cmd = ProjectStructureCommand()
        result = cmd.execute(mock_context)

        assert "Project Structure" in result
        assert "<pre>" in result
        mock_context.project_analyzer.get_project_structure.assert_called_once()


class TestReadFileCommand:

    def test_read_file_success(self, mock_context):
        mock_context.project_analyzer.read_file.return_value = "file content here"

        cmd = ReadFileCommand("test.gd")
        result = cmd.execute(mock_context)

        assert "test.gd" in result
        assert "file content here" in result
        assert "✓ File loaded" in result
        mock_context.project_analyzer.read_file.assert_called_once_with("test.gd")

        # Check that file was stored in context
        assert mock_context.assistant.last_read_file is not None
        assert mock_context.assistant.last_read_file["path"] == "test.gd"
        assert mock_context.assistant.last_read_file["content"] == "file content here"

    def test_read_file_not_found(self, mock_context):
        mock_context.project_analyzer.read_file.return_value = None

        cmd = ReadFileCommand("nonexistent.gd")

        with pytest.raises(FileNotFoundError) as exc_info:
            cmd.execute(mock_context)

        assert "nonexistent.gd" in str(exc_info.value)

    def test_read_large_file_truncated(self, mock_context):
        # Create a large file content (> 3000 chars)
        large_content = "x" * 5000
        mock_context.project_analyzer.read_file.return_value = large_content

        cmd = ReadFileCommand("large.gd")
        result = cmd.execute(mock_context)

        # Should show truncation message
        assert "showing first 3000 chars" in result


class TestListFilesCommand:

    def test_list_files_found(self, mock_context):
        mock_context.project_analyzer.find_files.return_value = ["file1.gd", "file2.gd"]

        cmd = ListFilesCommand("*.gd")
        result = cmd.execute(mock_context)

        assert "file1.gd" in result
        assert "file2.gd" in result
        assert "Files matching '*.gd'" in result
        mock_context.project_analyzer.find_files.assert_called_once_with("*.gd")

    def test_list_files_not_found(self, mock_context):
        mock_context.project_analyzer.find_files.return_value = []

        cmd = ListFilesCommand("*.xyz")

        with pytest.raises(ValueError) as exc_info:
            cmd.execute(mock_context)

        assert "No files found" in str(exc_info.value)

    def test_list_many_files_truncated(self, mock_context):
        # Create more than 50 files
        many_files = [f"file{i}.gd" for i in range(100)]
        mock_context.project_analyzer.find_files.return_value = many_files

        cmd = ListFilesCommand("*.gd")
        result = cmd.execute(mock_context)

        # Should show truncation message
        assert "and 50 more" in result


class TestClearContextCommand:

    def test_clear_with_context(self, mock_context):
        # Set up file context
        mock_context.assistant.last_read_file = {
            "path": "test.gd",
            "content": "content",
        }

        cmd = ClearContextCommand()
        result = cmd.execute(mock_context)

        assert "Cleared file context" in result
        assert "test.gd" in result
        assert mock_context.assistant.last_read_file is None

    def test_clear_without_context(self, mock_context):
        mock_context.assistant.last_read_file = None

        cmd = ClearContextCommand()
        result = cmd.execute(mock_context)

        assert "No file context to clear" in result


class TestLoreStatusCommand:

    def test_lore_directory_not_found(self, mock_context):
        mock_context.assistant.config.paths.lore_path = Path("/nonexistent")

        cmd = LoreStatusCommand()
        result = cmd.execute(mock_context)

        assert "not found" in result or "❌" in result

    def test_lore_directory_exists(self, mock_context, tmp_path):
        # Create temporary lore directory with files
        lore_dir = tmp_path / "lore"
        lore_dir.mkdir()
        (lore_dir / "story.txt").write_text("story content")

        mock_context.assistant.config.paths.lore_path = lore_dir

        cmd = LoreStatusCommand()
        result = cmd.execute(mock_context)

        assert "Lore Status" in result


class TestHelpCommand:

    def test_execute(self, mock_context):
        cmd = HelpCommand()
        result = cmd.execute(mock_context)

        assert "Available Commands" in result
        assert "/project info" in result
        assert "/read" in result
        assert "/list" in result


# Integration Tests
class TestCommandIntegration:

    def test_full_workflow_read_and_clear(self, mock_context, parser):
        # Setup
        mock_context.project_analyzer.read_file.return_value = "test content"

        # Parse and execute read command
        read_cmd = parser.parse("/read test.gd")
        read_result = read_cmd.execute(mock_context)

        # Verify file was loaded
        assert mock_context.assistant.last_read_file is not None
        assert "test content" in read_result

        # Parse and execute clear command
        clear_cmd = parser.parse("/clear")
        clear_result = clear_cmd.execute(mock_context)

        # Verify context was cleared
        assert mock_context.assistant.last_read_file is None
        assert "Cleared" in clear_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
