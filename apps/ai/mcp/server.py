"""MCP server implementation for the Django chat application.

This server provides tools, resources, and prompts for interacting with
the AI chat system through the Model Context Protocol.
"""

from typing import Any
from uuid import UUID

from mcp.server.fastmcp import Context, FastMCP

# Create the MCP server instance
mcp = FastMCP(
    "django-chat-mcp",
    instructions=(
        "This server provides access to the Django chat application's data and functionality. "
        "You can retrieve user information, access chat sessions and messages, "
        "and interact with the chat system."
    ),
)


# =============================================================================
# Tools - Functions that can be called by the AI
# =============================================================================


@mcp.tool()
def get_user_info(user_id: int) -> dict[str, Any]:
    """Get information about a user.

    Args:
        user_id: The ID of the user to retrieve

    Returns:
        Dictionary containing user information (id, username, email, names, active status)
    """
    from apps.common.models import User

    try:
        user = User.objects.get(id=user_id)
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
        }
    except User.DoesNotExist:
        return {"error": f"User with ID {user_id} not found"}


@mcp.tool()
async def get_chat_history(
    session_id: str, limit: int = 10, ctx: Context | None = None
) -> list[dict[str, Any]]:
    """Get chat message history for a session.

    Args:
        session_id: The UUID of the chat session
        limit: Maximum number of messages to return (default: 10)
        ctx: Optional context for progress tracking

    Returns:
        List of chat messages with role, content, and timestamp
    """
    from apps.ai.models import ChatMessage

    if ctx:
        await ctx.info(f"Retrieving chat history for session {session_id}")

    try:
        session_uuid = UUID(session_id)
    except ValueError:
        return {"error": f"Invalid session ID format: {session_id}"}

    messages = (
        ChatMessage.objects.filter(session__id=session_uuid)
        .order_by("-created_at")[:limit]
        .select_related("session")
    )

    return [
        {
            "id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat(),
            "is_processed": msg.is_processed,
        }
        for msg in reversed(messages)
    ]


@mcp.tool()
def list_user_sessions(user_id: int, limit: int = 20) -> list[dict[str, Any]]:
    """List all chat sessions for a specific user.

    Args:
        user_id: The ID of the user
        limit: Maximum number of sessions to return (default: 20)

    Returns:
        List of chat sessions with basic information
    """
    from apps.ai.models import ChatSession

    sessions = ChatSession.objects.filter(user_id=user_id).order_by("-modified_at")[
        :limit
    ]

    return [
        {
            "id": str(session.id),
            "title": session.title,
            "is_active": session.is_active,
            "message_count": session.message_count,
            "created_at": session.created_at.isoformat(),
            "modified_at": session.modified_at.isoformat(),
        }
        for session in sessions
    ]


@mcp.tool()
def get_session_stats(session_id: str) -> dict[str, Any]:
    """Get statistics about a chat session.

    Args:
        session_id: The UUID of the chat session

    Returns:
        Dictionary with session statistics (message counts, timestamps, etc.)
    """
    from apps.ai.models import ChatSession

    try:
        session_uuid = UUID(session_id)
        session = ChatSession.objects.get(id=session_uuid)

        message_counts = {
            "total": session.message_count,
            "user": session.messages.filter(role="user").count(),
            "assistant": session.messages.filter(role="assistant").count(),
            "system": session.messages.filter(role="system").count(),
        }

        return {
            "id": str(session.id),
            "title": session.title,
            "user_id": session.user_id,
            "is_active": session.is_active,
            "message_counts": message_counts,
            "created_at": session.created_at.isoformat(),
            "modified_at": session.modified_at.isoformat(),
            "last_message": (
                {
                    "role": session.last_message.role,
                    "content": session.last_message.content[:100],
                    "timestamp": session.last_message.created_at.isoformat(),
                }
                if session.last_message
                else None
            ),
        }
    except (ValueError, ChatSession.DoesNotExist):
        return {"error": f"Session {session_id} not found"}


# =============================================================================
# Resources - Data that can be read by the AI
# =============================================================================


@mcp.resource("chat://sessions")
def list_recent_sessions() -> str:
    """List the 20 most recent chat sessions across all users.

    Returns:
        Formatted string with session information
    """
    from apps.ai.models import ChatSession

    sessions = ChatSession.objects.all().order_by("-modified_at")[:20]

    result = "Recent Chat Sessions:\n\n"
    for session in sessions:
        result += f"- {session.id}: {session.title or 'Untitled'}\n"
        result += f"  User: {session.user.username if session.user else 'Anonymous'}\n"
        result += f"  Messages: {session.message_count}\n"
        result += f"  Last active: {session.modified_at.isoformat()}\n\n"

    return result


@mcp.resource("chat://sessions/{session_id}")
def get_session_details(session_id: str) -> str:
    """Get detailed information about a specific chat session.

    Args:
        session_id: The UUID of the chat session

    Returns:
        Formatted string with detailed session information
    """
    from apps.ai.models import ChatSession

    try:
        session_uuid = UUID(session_id)
        session = ChatSession.objects.get(id=session_uuid)

        result = f"Chat Session: {session.title or 'Untitled'}\n"
        result += f"ID: {session.id}\n"
        result += f"User: {session.user.username if session.user else 'Anonymous'}\n"
        result += f"Active: {session.is_active}\n"
        result += f"Messages: {session.message_count}\n"
        result += f"Created: {session.created_at.isoformat()}\n"
        result += f"Modified: {session.modified_at.isoformat()}\n\n"

        if session.last_message:
            result += f"Last Message ({session.last_message.role}):\n"
            result += f"{session.last_message.content[:200]}\n"

        return result
    except (ValueError, ChatSession.DoesNotExist):
        return f"Error: Session {session_id} not found"


@mcp.resource("chat://users/{user_id}/sessions")
def get_user_sessions(user_id: str) -> str:
    """Get all chat sessions for a specific user.

    Args:
        user_id: The ID of the user

    Returns:
        Formatted string with user's session information
    """
    from apps.ai.models import ChatSession

    try:
        user_id_int = int(user_id)
        sessions = ChatSession.objects.filter(user_id=user_id_int).order_by(
            "-modified_at"
        )[:50]

        result = f"Chat Sessions for User {user_id}:\n\n"
        for session in sessions:
            result += f"- {session.id}: {session.title or 'Untitled'}\n"
            result += f"  Messages: {session.message_count}\n"
            result += f"  Last active: {session.modified_at.isoformat()}\n\n"

        if not sessions:
            result += "No sessions found for this user.\n"

        return result
    except ValueError:
        return f"Error: Invalid user ID format: {user_id}"


# =============================================================================
# Prompts - Pre-configured prompts for common tasks
# =============================================================================


@mcp.prompt()
def chat_summary_prompt(session_id: str, detail_level: str = "brief") -> str:
    """Generate a prompt for summarizing a chat session.

    Args:
        session_id: The UUID of the chat session to summarize
        detail_level: Level of detail - "brief" or "detailed"

    Returns:
        Formatted prompt for the AI
    """
    if detail_level == "brief":
        return f"""
Please provide a brief summary of chat session {session_id}.
Include:
- Main topics discussed
- Key outcomes or decisions
- Overall sentiment
"""
    else:
        return f"""
Please provide a detailed analysis of chat session {session_id}.
Include:
- Comprehensive summary of all topics discussed
- Key questions asked and answers provided
- Any action items or follow-ups mentioned
- User's goals and how well they were addressed
- Suggestions for improving future interactions
"""


@mcp.prompt()
def user_analysis_prompt(user_id: str) -> str:
    """Generate a prompt for analyzing a user's chat patterns.

    Args:
        user_id: The ID of the user to analyze

    Returns:
        Formatted prompt for the AI
    """
    return f"""
Please analyze the chat patterns for user {user_id}.
Review their recent sessions and provide insights on:
- Common topics or questions
- Interaction patterns (frequency, length, complexity)
- Preferred communication style
- Areas where the assistant could provide better support
"""


@mcp.prompt()
def conversation_continuation_prompt(session_id: str) -> str:
    """Generate a prompt for continuing a conversation.

    Args:
        session_id: The UUID of the chat session to continue

    Returns:
        Formatted prompt for the AI
    """
    return f"""
Review the conversation history for session {session_id}.
Based on the context and the user's previous messages, suggest:
- Relevant follow-up questions the user might have
- Additional information that could be helpful
- Natural ways to continue or conclude the conversation
"""
