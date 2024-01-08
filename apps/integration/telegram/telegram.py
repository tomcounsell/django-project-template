from enum import Enum
import logging

from apps.communication.telegram.checks import checks_done
from apps.communication.telegram.utilities import handle_telegram_message

if not checks_done:
    raise RuntimeError("Checks not done")

from asgiref.sync import sync_to_async
from apps.communication.models import TelegramBotMembership
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class ChatState(Enum):
    DEFAULT = "default"
    TEXT = "text"
    PHOTO = "photo"
    END = ConversationHandler.END


async def text_response(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> ChatState:
    """Handles the default state where the user can say anything next."""

    response = await sync_to_async(handle_telegram_message)(update, context)

    await update.message.reply_text(response)
    return ChatState.TEXT


async def start_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> ChatState:
    """Starts the conversation."""
    await update.message.reply_text("My name is Steve and I'm here to help.")
    return ChatState.DEFAULT


async def end_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> ChatState:
    """Ends the conversation."""
    user = update.message.from_user
    logger.info("User %s ended the conversation.", user.first_name)
    await update.message.reply_text("K Bye!", reply_markup=ReplyKeyboardRemove())
    return ChatState.END


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_conversation)],
    states={
        ChatState.DEFAULT: [
            MessageHandler(filters.ALL, text_response),
        ],
        ChatState.TEXT: [
            MessageHandler(filters.ALL, text_response),
        ],
    },
    fallbacks=[CommandHandler("end", end_conversation)],
)
