# Documentation Plan: AI App & Safe Code Execution

## Overview

The AI app provides a comprehensive framework for integrating AI capabilities into Django applications. This includes pydantic-ai integration for agents, MCP (Model Context Protocol) server support, and notably, a safe code execution system for running LLM-generated code with proper sandboxing. This is a highly unique and security-critical feature.

## Target Audience

- Developers building AI-powered features
- Security engineers evaluating code execution safety
- Teams implementing agentic workflows
- Developers integrating with OpenAI, Anthropic, or other AI providers

## Documentation Structure

### 1. AI App Overview (1 page) ✅
- **Purpose** - Why a dedicated AI app exists ✅
- **Architecture** - How components fit together ✅
- **Key Features**: ✅
  - AI service integrations (OpenAI, Anthropic) ✅
  - Pydantic-AI agent framework ✅
  - MCP server support ✅
  - Safe code execution system ✅
  - Chat interface components ✅
- **When to Use** - Decision framework for AI features ✅

### 2. Pydantic-AI Integration (3 pages) ✅

#### 2.1 Overview ✅
- **What is Pydantic-AI?** - Type-safe AI agent framework ✅
- **Why Pydantic-AI?** - Benefits over raw API calls ✅
- **Configuration** - Setting up providers and models ✅

#### 2.2 Agent Framework ✅
- **Base Agent Structure** - `apps/ai/pydantic_ai/agent/` ✅
- **Chat Agent** - Building conversational agents ✅
- **Tools** - Adding tool capabilities to agents ✅
- **Simple Tools** - Quick tool definitions ✅

#### 2.3 LLM Providers ✅
- **Provider Abstraction** - `apps/ai/pydantic_ai/llm/providers.py` ✅
- **Supported Providers** - OpenAI, Anthropic, etc. ✅
- **Configuration** - API keys, model selection ✅
- **Switching Providers** - How to change models ✅

#### 2.4 Code Examples ✅
- Building a simple chat agent ✅
- Adding custom tools ✅
- Streaming responses ✅
- Error handling ✅

### 3. Safe Code Execution System (5 pages) ✅

> **Critical Security Feature** - This section requires extra attention as it deals with executing potentially dangerous LLM-generated code. ✅

#### 3.1 Security Philosophy ✅
- **Why Code Execution is Risky** - Attack vectors ✅
- **Defense in Depth** - Layered security approach ✅
- **Zero Trust for LLM Output** - Treat all generated code as untrusted ✅
- **Ephemeral Environments** - Destroy after execution ✅

#### 3.2 Architecture Overview ✅
- **Component Diagram** - How sandboxes, validators, executor interact ✅
- **Execution Flow** - From code submission to result ✅
- **Security Layers**: ✅
  1. Syntax validation ✅
  2. AST analysis ✅
  3. Sandbox execution ✅
  4. Output validation ✅

#### 3.3 Validators (`validators/`) ✅
- **Syntax Validator** - `syntax_validator.py` ✅
  - Basic Python syntax checking ✅
  - Early rejection of malformed code ✅
- **AST Validator** - `ast_validator.py` ✅
  - Dangerous pattern detection ✅
  - Import restrictions ✅
  - Function call restrictions ✅
  - Attribute access restrictions ✅
- **Output Validator** - `output_validator.py` ✅
  - Result sanitization ✅
  - Size limits ✅
  - Content filtering ✅

#### 3.4 Sandboxes (`sandboxes/`) ✅
- **Base Sandbox** - `base.py` interface ✅
- **RestrictedPython Sandbox** - `restricted_python.py` ✅
  - How RestrictedPython works ✅
  - Limitations and capabilities ✅
  - Custom guards and policies ✅
- **Future Sandboxes**: ✅
  - Docker-based execution ✅
  - gVisor integration ✅
  - WebAssembly sandboxing ✅

#### 3.5 Executor Service ✅
- **CodeExecutor** - `services/executor.py` ✅
- **Execution Pipeline**: ✅
  1. Receive code ✅
  2. Validate syntax ✅
  3. Validate AST ✅
  4. Execute in sandbox ✅
  5. Validate output ✅
  6. Return result ✅
- **Timeouts and Resource Limits** ✅
- **Error Handling** ✅

#### 3.6 Exceptions ✅
- **Custom Exceptions** - `exceptions.py` ✅
- **Security exceptions** - What triggers them ✅
- **User-facing vs. internal errors** ✅

#### 3.7 Security Testing ✅
- **Test Coverage** - `tests/test_security.py` ✅
- **Attack Vectors Tested**: ✅
  - System access attempts ✅
  - Import manipulation ✅
  - Eval/exec exploits ✅
  - Resource exhaustion ✅
  - Escape attempts ✅
- **Adding New Security Tests** ✅

#### 3.8 Production Recommendations ✅
- **When to use RestrictedPython** - Development, low-risk use cases ✅
- **When to upgrade to containers** - Production, untrusted users ✅
- **Monitoring and logging** ✅
- **Incident response** ✅

### 4. MCP Server (`mcp/`) ✅
- **What is MCP?** - Model Context Protocol overview ✅
- **Server Implementation** - `server.py` ✅
- **Exposing Django Data** - Making data available to AI ✅
- **Tool Registration** - Adding custom MCP tools ✅
- **Security Considerations** - Authentication, authorization ✅

### 5. Chat System (2 pages) ✅

#### 5.1 Models ✅
- **Chat Model** - `models/chat.py` ✅
- **Message storage** - How conversations are persisted ✅
- **User associations** ✅

#### 5.2 Views ✅
- **Chat View** - `views/chat.py` ✅
- **Test Views** - Development and testing pages ✅
- **HTMX Integration** - Real-time chat updates ✅

#### 5.3 Templates ✅
- **Chat Interface** - UI components ✅
- **Streaming Responses** - Displaying AI responses as they arrive ✅

### 6. Integration Examples (2 pages) ✅

#### 6.1 Building a Chat Feature ✅
- Complete walkthrough from scratch ✅
- Database models, views, templates ✅
- Streaming integration ✅

#### 6.2 Adding AI to Existing Features ✅
- Code review assistant example ✅
- Content generation example ✅
- Data analysis example ✅

#### 6.3 Safe Code Execution Use Cases ✅
- Code playground for users ✅
- AI-assisted calculations ✅
- Data transformation pipelines ✅

### 7. Testing AI Features (1 page) ✅
- **Mocking AI Providers** - Testing without API calls ✅
- **E2E Tests** - `test_e2e_chat.py`, `test_e2e_browser_chat.py` ✅
- **Security Tests** - Code execution safety ✅
- **Test Factories** - `tests/factories.py` ✅

## Content Sources

- Source code: `apps/ai/`
- Architecture doc: `docs/SAFE_LLM_CODE_EXECUTION_ARCHITECTURE.md`
- Tests: `apps/ai/tests/`, `apps/ai/code_execution/tests/`

## Implementation Notes

### Sphinx Integration
- Autodoc for all classes in `apps/ai/`
- Special attention to code execution security docs
- Cross-reference with integration docs (OpenAI settings)

### Security Documentation
- This is a security-critical feature
- Document all attack vectors and mitigations
- Include security checklist for deployers
- Regular security review reminders

### Warning Boxes
- Use prominent warnings for security-critical sections
- "Never run in production without container isolation"
- "RestrictedPython has known escape vectors"

## Estimated Effort

- Writing: 8-10 hours
- Code examples & testing: 3-4 hours
- Security review: 2 hours
- Diagrams (architecture, flow): 2 hours
- Sphinx integration: 1-2 hours
- Review & polish: 2 hours

**Total: 18-22 hours**

## Success Criteria

1. ✅ Security implications are crystal clear to any reader
2. ✅ Developers can implement safe code execution following the docs
3. ✅ All validators and sandboxes have complete API documentation
4. ✅ Attack vector tests are documented with explanations
5. ✅ Clear upgrade path from development sandbox to production container
6. ✅ Pydantic-AI integration is clear enough to build agents from scratch

## Implementation Status

**Status:** ✅ **COMPLETE**

**File Created:** `docs/source/guides/ai-features.rst`

**Date Completed:** 2026-01-31

The comprehensive AI features documentation has been successfully created with:

- Complete coverage of all planned sections
- Detailed security warnings and best practices
- Extensive code examples for all major features
- Clear upgrade path from development to production
- Cross-references to architecture documentation
- Troubleshooting guide and common patterns
- API reference links
- Contributing guidelines

The documentation emphasizes security throughout, with prominent warnings about the RestrictedPython sandbox limitations and clear guidance on production deployments with OS-level isolation.
