# Minimal Sphinx configuration for CI builds
import os
import sys

# Path setup
sys.path.insert(0, os.path.abspath('../../..'))

# Project information
project = 'Django Project Template'
copyright = '2025, Project Contributors'
author = 'Project Contributors'
release = '0.1.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Napoleon settings (for Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]
