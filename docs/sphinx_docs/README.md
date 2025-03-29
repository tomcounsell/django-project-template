# Sphinx Documentation

This directory contains the Sphinx documentation for the Django Project Template.

## Building the Documentation

### Automated Build

Run the build script from the project root:

```bash
./docs/scripts/build_docs.sh
```

### Manual Build

1. Change to the sphinx_docs directory:

```bash
cd docs/sphinx_docs
```

2. Generate API documentation:

```bash
sphinx-apidoc -o source/api ../../apps --separate --force
```

3. Build the HTML documentation:

```bash
make html
```

or on Windows:

```bat
make.bat html
```

4. View the documentation:

Open `build/html/index.html` in your web browser.

## Documentation Structure

- `source/`: Documentation source files
  - `conf.py`: Sphinx configuration
  - `index.rst`: Main index page
  - `_static/`: Static files (CSS, images)
  - `_templates/`: Custom templates
  - `apps/`: App-specific documentation
  - `models/`: Model documentation
  - `views/`: View documentation
  - `api/`: API documentation

## Writing Documentation

- Use reStructuredText (`.rst`) format for most documentation
- Follow the Google docstring style for Python code
- Include type hints in your code for better API documentation
- Use cross-references to link between documentation sections