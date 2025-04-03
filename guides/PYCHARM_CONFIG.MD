# PyCharm Development Configuration Guide

This document provides information about the PyCharm run configurations set up for the DeckFusion project.

## Available Run Configurations

The project includes several pre-configured run configurations to support different development workflows:

### HTTP-Only Configurations (Gunicorn/runserver)

- **Django Server**
  - Type: Django Server
  - Purpose: Standard Django development server with auto-reload
  - Command: `python manage.py runserver`
  - Best for: Basic development without WebSocket requirements

- **Run Tests**
  - Type: pytest
  - Purpose: Run project tests
  - Command: `pytest`
  - Best for: Test-driven development and verification

- **Lint Code**
  - Type: Shell
  - Purpose: Format and lint code
  - Command: `black . && isort . && mypy .`
  - Best for: Code quality checks before commits

### WebSocket Configurations (Daphne)

- **Daphne Server**
  - Type: Shell
  - Purpose: Run ASGI server that supports WebSockets
  - Command: `daphne -b 127.0.0.1 -p 8000 settings.asgi:application`
  - Best for: Basic WebSocket development without hot reload

- **Daphne Hot Reload**
  - Type: Shell
  - Purpose: Run Daphne with automatic reload on file changes
  - Command: Custom embedded script in the PyCharm run configuration
  - Best for: Active WebSocket development with hot reload
  - Note: Includes error detection logic to stop on crashes for easier debugging

### Background Tasks

- **Django Q Cluster**
  - Type: Python
  - Purpose: Run background task processor
  - Command: `python manage.py qcluster`
  - Best for: Testing background tasks and asynchronous operations

### CSS Development

- **Tailwind Watch**
  - Type: Python
  - Purpose: Compile Tailwind CSS in watch mode
  - Command: `python manage.py tailwind start`
  - Best for: Frontend CSS development

### Combined Development Environments

- **Run Full Stack**
  - Type: Compound
  - Purpose: Run Daphne and Django Q together
  - Components: Daphne Server + Django Q Cluster
  - Best for: Basic full-stack development

- **Dev Full Stack Hot Reload**
  - Type: Compound
  - Purpose: Run Daphne with hot reload and Django Q together
  - Components: Daphne Hot Reload + Django Q Cluster
  - Best for: Active backend development

- **Dev Complete Environment**
  - Type: Compound
  - Purpose: Complete development environment with hot reload
  - Components: Daphne Hot Reload + Django Q Cluster + Tailwind Watch
  - Best for: Full-stack development with all components

## Choosing the Right Configuration

### For HTTP-Only Development (Traditional Django)

If your current task doesn't require WebSockets:

1. Use **Django Server** for simple Django development
2. Combine with **Django Q Cluster** if background tasks are needed

### For WebSocket Development

When working with WebSockets (chat, live updates, etc.):

1. Use **Daphne Hot Reload** for active development
2. Combine with **Django Q Cluster** via **Dev Full Stack Hot Reload**
3. Add **Tailwind Watch** via **Dev Complete Environment** for full-stack work

## Hot Reload Setup

### Requirements

For optimal hot reload functionality:

1. Install watchdog: `pip install 'watchdog[watchmedo]'` (quotes are important for zsh compatibility)
2. Optionally install watchman for better performance: `brew install watchman`

### How Hot Reload Works

- **Python Files**: Automatically detected and trigger server restart
- **Templates**: Changes to HTML files trigger reload
- **Static Files**: No server restart needed, but browser refresh required
- **Tailwind CSS**: Automatically compiled when Tailwind Watch is running

### Error Handling

The Daphne Hot Reload configuration uses an embedded script with error detection:
- Initial validation: The script first tests if the server starts successfully
- Error detection: When the server crashes, the script terminates the watcher
- Clear feedback: Shows error messages with emoji indicators for better visibility
- Manual restart: After fixing errors, you'll need to manually restart the configuration

This approach provides these main advantages:
- Prevents endless error loops that make debugging difficult
- Shows the complete error traceback without it scrolling away
- Provides visual indicators of the server's status
- Everything is contained within the PyCharm configuration (no external files)

### Troubleshooting Hot Reload

If hot reload isn't working properly:

1. Ensure you're using the correct run configuration
2. Verify watchdog is installed correctly: `pip install 'watchdog[watchmedo]'` (note the single quotes)
3. If you get a "no matches found" error, it's likely a shell issue with square brackets; use quotes
4. Check terminal output for any errors
5. Try restarting PyCharm if necessary

#### Common ZSH Error

```
zsh: no matches found: watchdog[watchmedo]
```

This happens because zsh treats square brackets as a glob pattern. Solution:

- Always use single quotes around the package name: `pip install 'watchdog[watchmedo]'`
- Or escape the brackets: `pip install watchdog\[watchmedo\]`

## Deployment vs Development

These configurations are designed for local development. In production:

- **Gunicorn** serves HTTP traffic on Render (without WebSockets)
- **Daphne** serves both HTTP and WebSocket traffic (if configured)
- Redis is used for WebSocket channel layers in production
- Django Q tasks run in a separate worker process

## Adding Custom Configurations

To create additional configurations:

1. Go to Run → Edit Configurations...
2. Click the "+" button to add a new configuration
3. Select the appropriate configuration type
4. Configure settings and save with a descriptive name

## HTMX Integration with WebSockets

When using HTMX with WebSockets:

1. Include the WebSocket extension: `<script src="path/to/htmx-ws.js"></script>`
2. Use the `ws:` prefix for WebSocket endpoints: `hx-ws="connect:/chat"`
3. See WebSocket messages for partial DOM updates

For more details on HTMX WebSocket usage, see the [HTMX WebSocket documentation](https://htmx.org/extensions/web-sockets/).