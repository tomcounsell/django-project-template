"""
Tests for backward compatibility issues in the codebase.
The codebase should have no backward compatibility layers.
"""

import os
import re
from pathlib import Path
import pytest


def find_files_with_pattern(root_dir, pattern, file_extensions=None, exclude_dirs=None):
    """
    Find files containing a specific pattern.
    
    :param root_dir: Directory to start search from
    :param pattern: Regular expression pattern to search for
    :param file_extensions: List of file extensions to include (e.g., ['.py', '.html'])
    :param exclude_dirs: List of directory names to exclude
    :return: List of files that contain the pattern
    """
    matches = []
    
    if exclude_dirs is None:
        exclude_dirs = ['.git', 'node_modules', 'venv', '.venv', 'staticfiles']
    
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file_extensions and not any(file.endswith(ext) for ext in file_extensions):
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(pattern, content):
                        matches.append(file_path)
            except UnicodeDecodeError:
                # Skip binary files
                pass
    
    return matches


@pytest.mark.parametrize("pattern,description", [
    (r"backwards\s+compatibility", "Direct reference to backwards compatibility"),
    (r"legacy\s+support", "Legacy support reference"),
    (r"deprecated.*but\s+still\s+supported", "Deprecated but supported features"),
    (r"# For LOCAL mode \(kept for backwards compatibility\)", "LOCAL mode backwards compatibility"),
])
def test_no_backwards_compatibility_patterns(pattern, description):
    """Test that there are no backwards compatibility patterns in the codebase."""
    project_root = Path(__file__).parent.parent.parent.parent.parent
    file_extensions = ['.py', '.html', '.js', '.md']
    matches = find_files_with_pattern(project_root, pattern, file_extensions)
    
    # Special handling for tests like this one
    filtered_matches = [m for m in matches if 'test_backwards_compat.py' not in m]
    
    assert not filtered_matches, f"Found {description} in these files: {filtered_matches}"


@pytest.mark.parametrize("pattern,description,file_extensions", [
    (r"app_directories", "App-specific template directories", ['.py']),
    (r"django_components", "Django Components usage", ['.py']),
])
def test_no_legacy_patterns_in_settings(pattern, description, file_extensions):
    """Test that there are no legacy patterns in the settings files."""
    project_root = Path(__file__).parent.parent.parent.parent.parent
    settings_dir = project_root / 'settings'
    matches = find_files_with_pattern(settings_dir, pattern, file_extensions)
    
    assert not matches, f"Found {description} in these settings files: {matches}"