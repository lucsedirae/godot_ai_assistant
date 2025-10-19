# tests/conftest.py
"""
Pytest configuration and shared fixtures.
This file is automatically loaded by pytest.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))