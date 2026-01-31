=====================================
AI Features & Safe Code Execution
=====================================

Overview
========

The AI app provides a comprehensive framework for integrating AI capabilities into Django applications. It includes:

- **Pydantic-AI Integration**: Type-safe AI agent framework for building conversational agents
- **OpenAI Provider Support**: Simplified access to OpenAI models with best practices
- **Safe Code Execution**: Security-critical system for running LLM-generated code with proper sandboxing
- **Chat Interface**: Ready-to-use chat components and database models
- **MCP Server Support**: Model Context Protocol server for exposing Django data to AI agents

.. warning::
   **Security Critical Component**

   This app includes a safe code execution system for running LLM-generated code. While the system implements multiple security layers, **the included RestrictedPython sandbox is for development only** and should never be used in production with untrusted code.

   For production deployments, use OS-level isolation (E2B, gVisor, Firecracker, or similar).

Architecture
============

The AI app follows a layered architecture with clear separation of concerns:

.. code-block:: text

   ┌─────────────────────────────────────────────────────┐
   │  Application Layer (Django Views, APIs)             │
   └───────────────────┬─────────────────────────────────┘
                       │
   ┌───────────────────▼─────────────────────────────────┐
   │  Pydantic-AI Agents (Type-safe agent framework)     │
   │  - Chat agents with tools                           │
   │  - Provider abstraction (OpenAI, Anthropic, etc.)   │
   └───────────────────┬─────────────────────────────────┘
                       │
   ┌───────────────────▼─────────────────────────────────┐
   │  Safe Code Execution Pipeline                       │
   │  1. Syntax Validation                               │
   │  2. AST Security Analysis                           │
   │  3. Sandboxed Execution                             │
   │  4. Output Validation & Sanitization                │
   └─────────────────────────────────────────────────────┘

Core Components
===============

The AI app is organized into several key modules:

- ``pydantic_ai/``: PydanticAI agent framework and LLM provider integrations
- ``code_execution/``: Safe code execution system with validators, sandboxes, and executors
- ``models/``: Django models for chat sessions and messages
- ``views/``: Chat interface views and APIs
- ``mcp/``: Model Context Protocol server implementation

Pydantic-AI Integration
========================

The app uses `Pydantic-AI <https://ai.pydantic.dev/>`_ for building type-safe AI agents. Pydantic-AI provides:

- Type-safe agent definitions
- Automatic validation of inputs and outputs
- Tool integration for function calling
- Provider abstraction (OpenAI, Anthropic, etc.)
- Streaming response support

LLM Provider Configuration
---------------------------

The ``apps/ai/pydantic_ai/llm/providers.py`` module provides convenient functions for configuring OpenAI models:

.. code-block:: python

   from apps.ai.pydantic_ai.llm.providers import (
       get_openai_model,
       get_gpt_4_1_model,
       get_gpt_4o_model,
       get_gpt_4o_mini_model,
   )

   # Use default GPT-4.1 model
   model = get_gpt_4_1_model()

   # Or specify a custom model
   model = get_openai_model("gpt-4o", api_key="sk-...")

**Available Models:**

- ``gpt-4.1``: Best for tool use and agentic workflows (default)
- ``gpt-4o``: Balanced performance and cost
- ``gpt-4o-mini``: Cost-efficient for simple tasks

**Configuration:**

Set the ``OPENAI_API_KEY`` environment variable, or pass the API key directly:

.. code-block:: python

   # Via environment variable (recommended)
   export OPENAI_API_KEY=sk-...

   # Or pass directly
   model = get_openai_model("gpt-4.1", api_key="sk-...")

Building Chat Agents
--------------------

The ``apps/ai/pydantic_ai/agent/chat.py`` module provides a pre-configured chat agent with Python execution capabilities:

.. code-block:: python

   from apps.ai.pydantic_ai.agent.chat import (
       chat_agent,
       process_chat_message,
       ChatSession,
       ChatDependencies,
   )

   # Create a chat session
   session = ChatSession(
       session_id="unique-session-id",
       user_id=123,
   )

   # Process a message (async)
   response = await process_chat_message(
       message="What is 2 + 2?",
       session=session,
   )

   # Or use synchronous wrapper for Django views
   from apps.ai.pydantic_ai.agent.chat import process_chat_message_sync

   response = process_chat_message_sync(
       message="What is 2 + 2?",
       session=session,
   )

**Agent Tools:**

The default chat agent includes the ``run_python`` tool (from ``simple_tools.py``) which allows the agent to execute Python code safely. You can add custom tools:

.. code-block:: python

   from pydantic_ai import Agent, RunContext

   @chat_agent.tool
   async def search_database(ctx: RunContext[ChatDependencies], query: str) -> str:
       """Search the database for information."""
       # Your database search logic here
       return f"Results for: {query}"

**Custom System Prompts:**

The chat agent includes a dynamic system prompt that incorporates user context:

.. code-block:: python

   deps = ChatDependencies(
       user_id=123,
       session_id="abc",
       context={"role": "admin", "organization": "Acme Corp"}
   )

   response = await process_chat_message(
       message="Hello",
       session=session,
       deps=deps,
   )

Safe Code Execution System
===========================

.. danger::
   **CRITICAL SECURITY WARNING**

   The safe code execution system is designed to run potentially malicious LLM-generated code. The included ``RestrictedPythonSandbox`` is **NOT SECURE** for production use and should only be used for:

   - Development and testing
   - Running code from trusted users only
   - As an additional layer with OS-level isolation

   **For production, use OS-level isolation:**

   - E2B (recommended for managed solution)
   - gVisor containers
   - Firecracker microVMs
   - WebAssembly sandboxing

   See ``docs/SAFE_LLM_CODE_EXECUTION_ARCHITECTURE.md`` for detailed guidance.

Security Philosophy
-------------------

The code execution system implements **defense in depth** with multiple security layers:

1. **Syntax Validation**: Reject malformed code before execution
2. **AST Security Analysis**: Detect dangerous patterns in code structure
3. **Sandboxed Execution**: Run code in isolated environment with restricted capabilities
4. **Output Validation**: Sanitize results to prevent data exfiltration
5. **Resource Limits**: Prevent resource exhaustion attacks
6. **Comprehensive Logging**: Track all execution attempts for security monitoring

**Zero Trust for LLM Output:**

All LLM-generated code is treated as untrusted input. Even with multiple security layers, **never execute code without proper isolation**.

Execution Pipeline
------------------

The ``CodeExecutor`` class in ``apps/ai/code_execution/services/executor.py`` orchestrates the entire execution pipeline:

.. code-block:: python

   from apps.ai.code_execution import CodeExecutor

   # Create executor with default configuration
   executor = CodeExecutor(user_id=123)

   # Execute code
   result = executor.execute("""
   x = 1 + 1
   print(f"Result: {x}")
   """)

   # Check result
   if result.success:
       print(result.stdout)  # "Result: 2"
       print(f"Execution time: {result.execution_time_seconds}s")
   else:
       print(f"Error: {result.error_message}")
       if result.validation_violations:
           print(f"Violations: {result.validation_violations}")

**Execution Flow:**

1. Log execution attempt
2. Validate syntax (if enabled)
3. Analyze AST for security violations (if enabled)
4. Execute code in sandbox with timeout
5. Validate and sanitize output (if enabled)
6. Return comprehensive result with metadata

**Configuration Options:**

.. code-block:: python

   from apps.ai.code_execution import CodeExecutor, SandboxConfig

   # Custom configuration
   executor = CodeExecutor(
       user_id=123,
       sandbox_config=SandboxConfig(
           timeout_seconds=10,
           max_memory_mb=256,
           max_output_bytes=100_000,
           enable_network=False,
           allowed_imports=("math", "json", "datetime"),
       ),
       enable_syntax_validation=True,
       enable_ast_validation=True,
       enable_output_validation=True,
       redact_sensitive_output=True,
       log_executions=True,
   )

   # Execute with context data
   result = executor.execute(
       code="print(context['name'])",
       context={"name": "Alice", "age": 30}
   )

Validators
----------

Syntax Validator
~~~~~~~~~~~~~~~~

The ``SyntaxValidator`` in ``apps/ai/code_execution/validators/syntax_validator.py`` performs basic Python syntax checking using the ``ast`` module:

.. code-block:: python

   from apps.ai.code_execution.validators import SyntaxValidator

   validator = SyntaxValidator()
   result = validator.validate("print('hello')")

   if result.is_valid:
       print("Code is syntactically valid")
   else:
       print(f"Syntax error: {result.error_message}")
       print(f"Line {result.line_number}, column {result.offset}")

**Features:**

- Detects syntax errors before execution
- Provides line numbers and error details
- Zero false positives (uses Python's own parser)
- Thread-safe and stateless

AST Security Validator
~~~~~~~~~~~~~~~~~~~~~~

The ``ASTValidator`` in ``apps/ai/code_execution/validators/ast_validator.py`` analyzes code structure to detect dangerous patterns:

.. code-block:: python

   from apps.ai.code_execution.validators import ASTValidator

   validator = ASTValidator()
   violations = validator.validate("import os; os.system('ls')")

   for v in violations:
       print(f"{v.severity}: {v.message} on line {v.line_number}")
       print(f"  Type: {v.violation_type}")

   # high: Import of 'os' is not allowed on line 1
   #   Type: forbidden_import

**Detected Patterns:**

- **Forbidden Imports**: ``os``, ``sys``, ``subprocess``, ``socket``, ``pickle``, etc.
- **Dangerous Functions**: ``eval``, ``exec``, ``compile``, ``open``, ``__import__``
- **Dangerous Attributes**: ``__builtins__``, ``__globals__``, ``__subclasses__``, ``__code__``
- **Code Complexity**: Maximum number of AST operations

**Default Forbidden Imports:**

.. code-block:: python

   FORBIDDEN_IMPORTS = {
       # System access
       "os", "sys", "pathlib", "subprocess", "shutil", "glob",
       # Network
       "socket", "urllib", "requests", "http", "httpx",
       # Database
       "sqlite3", "dbm", "shelve",
       # Serialization (code execution risk)
       "pickle", "marshal", "dill",
       # Concurrency
       "threading", "multiprocessing", "asyncio",
       # Dynamic code
       "importlib", "imp", "runpy",
       # File I/O
       "io", "tempfile",
       # Other dangerous modules
       "ctypes", "gc", "inspect", "code",
   }

**Custom Configuration:**

.. code-block:: python

   validator = ASTValidator(
       forbidden_imports={"os", "sys", "subprocess"},
       forbidden_functions={"eval", "exec"},
       max_operations=5000,
       allow_getattr=True,  # Allow getattr for data access
       allow_setattr=False,  # Disallow setattr
   )

Output Validator
~~~~~~~~~~~~~~~~

The ``OutputValidator`` in ``apps/ai/code_execution/validators/output_validator.py`` sanitizes execution output to prevent data exfiltration:

.. code-block:: python

   from apps.ai.code_execution.validators import OutputValidator

   validator = OutputValidator(
       max_output_bytes=100_000,
       redact=True,  # Automatically redact sensitive data
       strict=False,  # Only reject on high-severity violations
   )

   result = validator.validate("API Key: sk-abc123...")

   print(result.sanitized_output)  # "API Key: [REDACTED]"
   print(result.was_redacted)  # True
   print(result.violations)  # List of detected patterns

**Detected Patterns:**

- Social Security Numbers (SSN)
- Credit card numbers
- Email addresses (low severity, often legitimate)
- AWS access keys and secret keys
- OpenAI API keys
- Generic API keys and secrets
- Private key headers
- Database connection strings

**Size Limits:**

Output exceeding ``max_output_bytes`` is automatically truncated with a warning message.

Sandboxes
---------

Base Sandbox Interface
~~~~~~~~~~~~~~~~~~~~~~

All sandboxes implement the ``BaseSandbox`` interface defined in ``apps/ai/code_execution/sandboxes/base.py``:

.. code-block:: python

   from apps.ai.code_execution.sandboxes import BaseSandbox, SandboxConfig, SandboxResult

   class MySandbox(BaseSandbox):
       def execute(self, code: str, config: SandboxConfig) -> SandboxResult:
           # 1. Set up isolated environment
           # 2. Apply resource limits
           # 3. Execute code with timeout
           # 4. Capture output
           # 5. Return result
           pass

       def cleanup(self):
           # Clean up resources
           pass

**SandboxConfig:**

.. code-block:: python

   config = SandboxConfig(
       timeout_seconds=30.0,
       max_memory_mb=512,
       max_output_bytes=1_000_000,
       enable_network=False,
       allowed_imports=("math", "json", "re", "datetime"),
       execution_context={"user": "Alice"},
       user_id=123,
   )

**SandboxResult:**

.. code-block:: python

   result = SandboxResult(
       success=True,
       stdout="Output here",
       stderr="",
       return_value=None,
       error_message=None,
       error_type=None,
       execution_time_seconds=0.05,
       memory_used_mb=32.5,
       exit_code=0,
       metadata={"sandbox_type": "RestrictedPython"},
   )

RestrictedPython Sandbox
~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   **DEVELOPMENT ONLY - NOT PRODUCTION READY**

   The ``RestrictedPythonSandbox`` uses pure Python mechanisms and is **NOT SECURE** for production use. Known escape vectors exist using Python's introspection capabilities.

   **Appropriate use cases:**

   - Local development and testing
   - Running code from trusted users only
   - As an additional layer with OS-level isolation

   **Never use for:**

   - Production with untrusted code
   - User-facing applications
   - Adversarial scenarios
   - Anything involving sensitive data

The ``RestrictedPythonSandbox`` in ``apps/ai/code_execution/sandboxes/restricted_python.py`` provides a proof-of-concept implementation using Python's restricted execution features:

.. code-block:: python

   from apps.ai.code_execution.sandboxes import RestrictedPythonSandbox, SandboxConfig

   sandbox = RestrictedPythonSandbox()
   config = SandboxConfig(timeout_seconds=10)

   result = sandbox.execute(
       code="print('Hello, World!')",
       config=config
   )

   print(result.stdout)  # "Hello, World!"
   sandbox.cleanup()

**Security Mechanisms:**

1. **Custom Import Function**: Blocks dangerous modules at import time
2. **Restricted Builtins**: Only safe built-in functions available
3. **Namespace Isolation**: Code runs in restricted global namespace
4. **Timeout Enforcement**: Uses SIGALRM on Unix systems (not available on Windows)
5. **Output Capture**: Redirects stdout/stderr to prevent console pollution
6. **Pre-imported Safe Libraries**: math, json, re, datetime, collections (if allowed)

**Known Limitations:**

- Can be escaped via ``object.__subclasses__()`` to find unrestricted classes
- Can access ``__import__`` through object introspection
- Can access frame objects to escape namespace restrictions
- Many other documented escape techniques
- Timeout not enforced on Windows (no SIGALRM)
- Pure Python code in tight loops may not respond to signals

**Blocked Modules:**

.. code-block:: python

   BLOCKED_MODULES = {
       "os", "sys", "pathlib", "subprocess", "shutil", "glob",
       "socket", "urllib", "requests", "http", "ftplib", "smtplib",
       "sqlite3", "dbm", "shelve",
       "pickle", "marshal",
       "threading", "multiprocessing", "asyncio",
       "importlib", "imp", "runpy",
       "io", "tempfile",
       "ctypes", "gc", "inspect", "code", "codeop",
   }

Future Sandbox Implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For production use, consider implementing sandboxes using:

**Docker with gVisor:**

- Intercepts all system calls
- Implements Linux kernel in memory-safe Go
- Strong isolation without full virtualization overhead
- Used by E2B for LLM agent sandboxing

**Firecracker MicroVMs:**

- Hardware virtualization (KVM)
- Starts in ~125ms
- <5 MiB memory overhead
- Powers AWS Lambda and Fargate
- Guest kernel itself treated as untrusted

**WebAssembly (Wasm):**

- Memory isolation with bounds-checked linear memory
- Control flow integrity
- Capability-based security model (WASI)
- Deny-by-default access
- Provably-safe sandboxing

See ``docs/SAFE_LLM_CODE_EXECUTION_ARCHITECTURE.md`` for implementation details.

Exception Handling
------------------

The ``apps/ai/code_execution/exceptions.py`` module defines a hierarchy of exceptions for different failure modes:

.. code-block:: python

   from apps.ai.code_execution.exceptions import (
       CodeExecutionError,      # Base exception
       ValidationError,          # Pre-execution validation failed
       SandboxError,             # Sandbox environment failure
       TimeoutError,             # Execution exceeded time limit
       ResourceLimitError,       # Resource limits exceeded
       SecurityViolationError,   # Prohibited operation attempted
       OutputValidationError,    # Output validation failed
   )

**Exception Attributes:**

All exceptions include:

- ``message``: Human-readable error description
- ``details``: Additional context (dict)
- ``can_retry``: Whether the operation might succeed if retried

**Converting to JSON:**

.. code-block:: python

   try:
       result = executor.execute(code)
   except CodeExecutionError as e:
       error_data = e.to_dict()
       # {
       #     "error_type": "SecurityViolationError",
       #     "message": "Import blocked: os",
       #     "details": {"violation_type": "blocked_import"},
       #     "can_retry": False
       # }

**SecurityViolationError:**

.. warning::
   Security violations should be logged with high priority as they may indicate:

   - LLM prompt injection attacks
   - Deliberate security probing
   - Need to update blocked module list

   These should NOT be retried without security review.

Security Testing
----------------

The ``apps/ai/code_execution/tests/test_security.py`` module contains comprehensive security tests that attempt to bypass sandbox restrictions:

**Test Categories:**

1. **Import Restrictions**: Verify dangerous imports are blocked
2. **Function Restrictions**: Block eval, exec, compile, open
3. **Attribute Access**: Block __builtins__, __globals__, __subclasses__
4. **Resource Exhaustion**: Timeout infinite loops, limit output size
5. **Data Exfiltration**: Detect and redact sensitive data in output
6. **Escape Attempts**: Test known Python sandbox escape techniques
7. **Legitimate Code**: Ensure security measures don't break valid use cases

**Running Security Tests:**

.. code-block:: bash

   # Run all security tests
   pytest apps/ai/code_execution/tests/test_security.py -v

   # Run specific test class
   pytest apps/ai/code_execution/tests/test_security.py::TestImportRestrictions -v

   # Run with coverage
   pytest apps/ai/code_execution/tests/test_security.py --cov=apps.ai.code_execution

**Example Security Test:**

.. code-block:: python

   def test_block_os_import(self):
       """Should block import of os module."""
       executor = CodeExecutor()
       result = executor.execute("import os")

       assert not result.success or result.validation_violations
       # Should be caught by AST validator before execution

   def test_detect_api_key_in_output(self):
       """Should detect API keys in output."""
       executor = CodeExecutor(redact_sensitive_output=True)
       result = executor.execute('''
   api_key = "sk-abc123def456ghi789jkl012mno345pqr678stu901vwx234"
   print(f"API Key: {api_key}")
   ''')

       assert result.success
       assert "sk-abc123" not in result.stdout  # Should be redacted
       assert result.output_violations
       assert result.was_output_redacted

**Adding New Security Tests:**

When adding new security measures, always add corresponding tests:

.. code-block:: python

   def test_block_new_dangerous_module(self):
       """Should block import of newly identified dangerous module."""
       executor = CodeExecutor()
       result = executor.execute("import dangerous_module")

       assert not result.success or result.validation_violations
       assert any(
           "dangerous_module" in str(v)
           for v in result.validation_violations
       )

Production Recommendations
--------------------------

.. danger::
   **Before deploying code execution to production:**

**When to use RestrictedPython:**

- Local development only
- Testing the executor architecture
- Running code from authenticated, trusted users in controlled environments
- As an ADDITIONAL layer with OS-level isolation

**When to upgrade to containers/VMs:**

- Production deployments
- Untrusted user input
- Multi-tenant applications
- Anything involving sensitive data
- Compliance requirements

**Security Checklist:**

Before production deployment, ensure:

☐ OS-level isolation implemented (E2B, gVisor, Firecracker, or Wasm)
☐ All resource limits enabled and tested
☐ Network access disabled by default
☐ Comprehensive logging and monitoring configured
☐ Audit trail for all executions
☐ Rate limiting per user implemented
☐ Alerts configured for suspicious activity
☐ Security tests passing
☐ Incident response procedures documented
☐ Regular security audits scheduled
☐ Dependency scanning enabled
☐ Compliance requirements met (GDPR, PCI-DSS, HIPAA, etc.)

**Monitoring and Logging:**

.. code-block:: python

   # Configure structured logging
   import logging

   logger = logging.getLogger("apps.ai.code_execution")
   logger.setLevel(logging.INFO)

   # The CodeExecutor logs:
   # - All execution attempts (user_id, code_length, context)
   # - Execution results (success/failure, timing, violations)
   # - High-priority alerts for security violations

**Recommended Monitoring:**

- Execution success/failure rates
- Average execution time
- Resource usage trends
- Security violation frequency
- User-specific patterns (potential abuse detection)
- Failed execution reasons

**Incident Response:**

1. **Detection**: Automated alerts for high-severity violations
2. **Assessment**: Review logs to determine attack scope
3. **Containment**: Rate limit or disable user accounts if needed
4. **Investigation**: Analyze attack vectors and update security measures
5. **Recovery**: Update validators and sandbox configurations
6. **Lessons Learned**: Document and share findings with team

Chat System
===========

The AI app includes a complete chat system with database models, views, and templates.

Database Models
---------------

The ``apps/ai/models/chat.py`` module defines Django models for chat functionality:

**ChatSession Model:**

.. code-block:: python

   from apps.ai.models import ChatSession, ChatMessage

   # Create a new chat session
   session = ChatSession.objects.create(
       user=request.user,
       title="My Chat",
       is_active=True,
       metadata={"model": "gpt-4.1"},
   )

   # Access session properties
   print(session.message_count)  # Number of messages
   print(session.last_message)   # Most recent message
   print(session.generate_title())  # Auto-generate title from first message

**ChatMessage Model:**

.. code-block:: python

   # Add messages to session
   user_msg = ChatMessage.objects.create(
       session=session,
       role="user",
       content="What is Django?",
       metadata={"client_ip": "192.168.1.1"},
   )

   assistant_msg = ChatMessage.objects.create(
       session=session,
       role="assistant",
       content="Django is a high-level Python web framework...",
       metadata={"model": "gpt-4.1", "tokens": 150},
   )

**Model Fields:**

- ``session.id``: UUID primary key
- ``session.user``: ForeignKey to User (nullable)
- ``session.title``: Optional title for the session
- ``session.is_active``: Whether session is currently active
- ``session.metadata``: JSON field for additional data
- ``message.role``: "user", "assistant", or "system"
- ``message.content``: Message text
- ``message.metadata``: JSON field (e.g., model, tokens, timing)

Chat Views
----------

The ``apps/ai/views/chat.py`` module provides views for the chat interface:

.. code-block:: python

   from django.shortcuts import render
   from apps.ai.models import ChatSession
   from apps.ai.pydantic_ai.agent.chat import process_chat_message_sync

   def chat_view(request):
       # Get or create session
       session_id = request.session.get("chat_session_id")
       if session_id:
           session = ChatSession.objects.get(id=session_id)
       else:
           session = ChatSession.objects.create(user=request.user)
           request.session["chat_session_id"] = str(session.id)

       if request.method == "POST":
           user_message = request.POST.get("message")

           # Process with AI
           response = process_chat_message_sync(
               message=user_message,
               session=session,
           )

           # Messages are automatically saved by process_chat_message_sync

       messages = session.messages.all()
       return render(request, "ai/chat.html", {
           "session": session,
           "messages": messages,
       })

**Test Views:**

Development views are available for testing:

- ``/ai/test/chat/``: Test chat interface
- ``/ai/test/page/``: Test page with chat component

Integration with Django
========================

Using Code Execution in Views
------------------------------

.. code-block:: python

   from django.http import JsonResponse
   from django.views.decorators.http import require_POST
   from apps.ai.code_execution import CodeExecutor

   @require_POST
   def execute_code(request):
       code = request.POST.get("code")

       if not code:
           return JsonResponse({"error": "No code provided"}, status=400)

       # Create executor
       executor = CodeExecutor(
           user_id=request.user.id if request.user.is_authenticated else None,
           enable_ast_validation=True,
           enable_output_validation=True,
           redact_sensitive_output=True,
       )

       # Execute code
       result = executor.execute(code)

       # Return result as JSON
       return JsonResponse(result.to_dict())

Using Chat Agents in Views
---------------------------

.. code-block:: python

   from django.views.generic import TemplateView
   from apps.ai.pydantic_ai.agent.chat import (
       process_chat_message_sync,
       ChatSession,
   )

   class ChatView(TemplateView):
       template_name = "chat.html"

       def post(self, request):
           message = request.POST.get("message")
           session_id = request.session.get("ai_session_id")

           # Get or create Pydantic session (in-memory)
           if session_id and session_id in self.cached_sessions:
               session = self.cached_sessions[session_id]
           else:
               session = ChatSession(
                   session_id=str(uuid.uuid4()),
                   user_id=request.user.id,
               )
               self.cached_sessions[session.session_id] = session
               request.session["ai_session_id"] = session.session_id

           # Process message
           response = process_chat_message_sync(message, session)

           return JsonResponse({
               "response": response,
               "session_id": session.session_id,
           })

Async Support with Celery
--------------------------

For long-running executions, use Celery tasks:

.. code-block:: python

   # apps/ai/tasks.py
   from celery import shared_task
   from apps.ai.code_execution import CodeExecutor

   @shared_task(
       bind=True,
       max_retries=3,
       time_limit=120,
   )
   def execute_code_async(self, code, user_id=None):
       """Execute code asynchronously."""
       executor = CodeExecutor(user_id=user_id)

       try:
           result = executor.execute(code)
           return result.to_dict()
       except Exception as exc:
           raise self.retry(exc=exc, countdown=5)

   # In your view
   from apps.ai.tasks import execute_code_async

   def submit_code(request):
       code = request.POST.get("code")

       # Submit to Celery
       task = execute_code_async.delay(
           code=code,
           user_id=request.user.id,
       )

       return JsonResponse({
           "task_id": task.id,
           "status": "pending",
       })

MCP Server Support
==================

The AI app includes Model Context Protocol (MCP) server support for exposing Django data to AI agents.

MCP allows AI agents to:

- Access your Django models and data
- Execute database queries
- Perform CRUD operations
- Access custom business logic

**Location:** ``apps/ai/mcp/server.py``

See the MCP documentation for setup and configuration details.

Best Practices
==============

Code Execution Security
-----------------------

1. **Always validate before execution**: Enable syntax and AST validation
2. **Limit resources**: Set appropriate timeout, memory, and output limits
3. **Redact sensitive output**: Enable output validation and redaction
4. **Log all executions**: Track who executed what and when
5. **Use OS-level isolation in production**: Never rely on pure Python sandboxing
6. **Monitor for anomalies**: Set up alerts for suspicious patterns
7. **Rate limit per user**: Prevent abuse and resource exhaustion
8. **Review logs regularly**: Especially security violations

Model Selection
---------------

Choose the right model for your use case:

- **GPT-4.1**: Best for tool use, agentic workflows, complex reasoning
- **GPT-4o**: Balanced performance and cost for general tasks
- **GPT-4o-mini**: Cost-efficient for simple tasks, high-volume workloads

Prompt Engineering
------------------

1. **Be specific**: Clear instructions produce better results
2. **Provide context**: Use the execution context for user-specific data
3. **Use system prompts**: Configure agent behavior with system prompts
4. **Test iteratively**: Refine prompts based on actual results
5. **Handle errors gracefully**: Provide fallback responses

Chat Interface Design
---------------------

1. **Show streaming responses**: Use HTMX for real-time updates
2. **Persist conversations**: Save to database for history
3. **Handle failures**: Display error messages clearly
4. **Add feedback mechanisms**: Let users rate responses
5. **Include loading states**: Show when AI is thinking

Monitoring and Observability
-----------------------------

Track key metrics:

- **Execution metrics**: Success rate, average time, resource usage
- **Security metrics**: Validation failures, security violations
- **Cost metrics**: Token usage, model costs
- **User metrics**: Active sessions, messages per user

Error Handling
--------------

.. code-block:: python

   from apps.ai.code_execution import CodeExecutor
   from apps.ai.code_execution.exceptions import (
       ValidationError,
       TimeoutError,
       SecurityViolationError,
   )

   executor = CodeExecutor()

   try:
       result = executor.execute(code)
   except ValidationError as e:
       # Code failed validation
       logger.warning(f"Validation failed: {e.message}", extra=e.details)
   except TimeoutError as e:
       # Execution took too long
       logger.warning(f"Timeout: {e.message}")
   except SecurityViolationError as e:
       # Security violation detected
       logger.error(
           f"SECURITY VIOLATION: {e.message}",
           extra=e.details,
       )
       # Alert security team
   except Exception as e:
       # Unexpected error
       logger.exception("Unexpected error during code execution")

Common Patterns
===============

Data Analysis with Code Execution
----------------------------------

.. code-block:: python

   def analyze_data(request):
       data = request.POST.get("data")  # CSV or JSON
       analysis_code = request.POST.get("code")

       executor = CodeExecutor()
       result = executor.execute(
           code=analysis_code,
           context={
               "data": data,
               "user_id": request.user.id,
           }
       )

       return JsonResponse({
           "result": result.stdout,
           "visualization": result.return_value,
       })

Building a Code Playground
---------------------------

.. code-block:: python

   class CodePlaygroundView(TemplateView):
       template_name = "playground.html"

       def post(self, request):
           code = request.POST.get("code")

           executor = CodeExecutor(
               user_id=request.user.id,
               sandbox_config=SandboxConfig(
                   timeout_seconds=5,
                   max_memory_mb=256,
                   allowed_imports=("math", "json", "datetime", "re"),
               ),
           )

           result = executor.execute(code)

           return JsonResponse({
               "success": result.success,
               "output": result.stdout,
               "error": result.error_message,
               "time": result.execution_time_seconds,
           })

AI-Assisted Calculations
-------------------------

.. code-block:: python

   async def ai_calculator(user_question: str) -> str:
       """Use AI to interpret question and generate calculation code."""
       from apps.ai.pydantic_ai.agent.chat import chat_agent

       result = await chat_agent.run(
           f"Calculate this and show your work: {user_question}"
       )

       # The chat agent will use run_python tool automatically
       return result.data

Troubleshooting
===============

Common Issues
-------------

**Issue: "Import of 'os' is not allowed"**

This is expected behavior - the ``os`` module is blocked for security. Use allowed modules like ``math``, ``json``, ``datetime`` instead.

**Issue: Code execution times out**

- Increase timeout in ``SandboxConfig``
- Check for infinite loops
- Optimize the code for performance
- Consider breaking into smaller executions

**Issue: Output is truncated**

Increase ``max_output_bytes`` in ``SandboxConfig``:

.. code-block:: python

   config = SandboxConfig(max_output_bytes=5_000_000)  # 5 MB

**Issue: "Output validation failed"**

Check if sensitive data is in the output:

.. code-block:: python

   executor = CodeExecutor(
       enable_output_validation=True,
       redact_sensitive_output=True,  # Auto-redact instead of failing
   )

**Issue: Sandbox escape detected**

This is a critical security event:

1. Review logs immediately
2. Examine the code that triggered it
3. Update validators if new pattern detected
4. Consider upgrading to OS-level isolation

Debugging
---------

Enable detailed logging:

.. code-block:: python

   import logging

   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger("apps.ai.code_execution")
   logger.setLevel(logging.DEBUG)

   # Now all execution details will be logged

Check execution result details:

.. code-block:: python

   result = executor.execute(code)

   print(f"Success: {result.success}")
   print(f"Stdout: {result.stdout}")
   print(f"Stderr: {result.stderr}")
   print(f"Error: {result.error_message}")
   print(f"Violations: {result.validation_violations}")
   print(f"Output violations: {result.output_violations}")
   print(f"Time: {result.execution_time_seconds}s")
   print(f"Total time: {result.total_time_seconds}s")
   print(f"Metadata: {result.sandbox_metadata}")

Additional Resources
====================

Architecture Documentation
--------------------------

For detailed security architecture and production deployment guidance:

``docs/SAFE_LLM_CODE_EXECUTION_ARCHITECTURE.md``

This document covers:

- OS-level isolation strategies (gVisor, Firecracker, WebAssembly)
- Production-ready tools (E2B, CodeJail, Judge0)
- Security best practices and OWASP guidelines
- Resource limitation strategies
- Multi-tenant isolation patterns
- Comprehensive implementation examples

External Documentation
----------------------

- `Pydantic-AI Documentation <https://ai.pydantic.dev/>`_
- `OpenAI API Reference <https://platform.openai.com/docs/api-reference>`_
- `OWASP Top 10 for LLM Applications <https://owasp.org/www-project-top-10-for-large-language-model-applications/>`_
- `E2B - Sandboxes for AI Agents <https://e2b.dev/>`_
- `gVisor - Container Security Platform <https://gvisor.dev/>`_
- `RestrictedPython Documentation <https://restrictedpython.readthedocs.io/>`_

Code Examples
-------------

Complete working examples can be found in:

- ``apps/ai/tests/test_e2e_chat.py``: End-to-end chat tests
- ``apps/ai/tests/test_e2e_browser_chat.py``: Browser-based chat tests
- ``apps/ai/code_execution/tests/test_security.py``: Security test suite
- ``apps/ai/views/test_chat.py``: Test chat views

API Reference
=============

For detailed API documentation of all classes and functions, see the autodoc-generated pages:

- :doc:`/api/ai/code_execution`
- :doc:`/api/ai/pydantic_ai`
- :doc:`/api/ai/models`
- :doc:`/api/ai/views`

Contributing
============

Security Issues
---------------

If you discover a security vulnerability in the code execution system:

1. **Do NOT open a public issue**
2. Email the security team directly
3. Provide detailed reproduction steps
4. Include affected versions

We will respond promptly and coordinate disclosure.

Adding New Features
-------------------

When adding features to the AI app:

1. **Add tests**: Especially security tests for code execution features
2. **Update documentation**: Keep this guide up to date
3. **Follow security best practices**: Use defense in depth
4. **Get security review**: For anything touching code execution
5. **Update changelog**: Document changes

Contributing Tests
------------------

We especially welcome:

- New security test cases
- Escape technique tests
- Performance benchmarks
- Integration tests

License
=======

This AI app and documentation are part of the django-project-template and inherit its license.
