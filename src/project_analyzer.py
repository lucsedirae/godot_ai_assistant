# src/project_analyzer.py
import os
from pathlib import Path


class ProjectAnalyzer:
    """Analyzes and provides context about the user's Godot project"""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.project_exists = self.project_path.exists()

    def get_project_structure(self, max_depth=3):
        """Get a tree-like structure of the project"""
        if not self.project_exists:
            return "No project mounted"

        structure = []
        structure.append(f"Project root: {self.project_path}")

        try:
            for root, dirs, files in os.walk(self.project_path):
                level = root.replace(str(self.project_path), "").count(os.sep)
                if level >= max_depth:
                    dirs[:] = []  # Don't go deeper
                    continue

                indent = " " * 2 * level
                structure.append(f"{indent}{os.path.basename(root)}/")

                subindent = " " * 2 * (level + 1)
                for file in sorted(files)[:10]:  # Limit files per directory
                    if file.endswith((".gd", ".tscn", ".tres", ".godot")):
                        structure.append(f"{subindent}{file}")

            return "\n".join(structure[:100])  # Limit total lines
        except Exception as e:
            return f"Error reading project: {e}"

    def read_file(self, relative_path):
        """Read a file from the project"""
        try:
            file_path = self.project_path / relative_path
            if not file_path.exists():
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def find_files(self, pattern="*.gd"):
        """Find files matching a pattern"""
        if not self.project_exists:
            return []

        try:
            return [
                str(p.relative_to(self.project_path))
                for p in self.project_path.rglob(pattern)
            ][:50]
        except Exception as e:
            return []

    def get_project_info(self):
        """Get basic project information"""
        if not self.project_exists:
            return "No Godot project is currently mounted."

        info = []
        info.append(f"Project location: {self.project_path}")

        # Check for project.godot
        project_file = self.project_path / "project.godot"
        if project_file.exists():
            info.append("✓ Valid Godot project detected (project.godot found)")
        else:
            info.append("⚠ No project.godot found - may not be a Godot project root")

        # Count files
        gd_files = len(self.find_files("*.gd"))
        scene_files = len(self.find_files("*.tscn"))

        info.append(f"GDScript files: {gd_files}")
        info.append(f"Scene files: {scene_files}")

        return "\n".join(info)
