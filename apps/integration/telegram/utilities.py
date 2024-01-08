from typing import Dict

import requests
from telegram import Update
from telegram.ext import CallbackContext

from ai.conversation import Conversation
from apps.communication.models import TelegramBotMembership

global telegram_bot_membership_conversations
telegram_bot_membership_conversations: Dict[int, Conversation] = (
    telegram_bot_membership_conversations or dict()
)


class TelegramBotException(Exception):
    def __init__(self, user_message="", developer_message=""):
        self.user_message = user_message
        self.developer_message = developer_message


def handle_telegram_message(update: Update, context: CallbackContext):
    # get user membership
    telegram_bot_membership, um_created = TelegramBotMembership.objects.get_or_create(
        telegram_user_id=str(update.message.from_user.id)
    )
    if not update.message.text:
        return "just text chat for now pls"

    text_response = ""

    # get conversations from global scope dict
    global telegram_bot_membership_conversations
    conversation = telegram_bot_membership_conversations.get(telegram_bot_membership.id)
    if not conversation:
        text_response = "Hi, I'm Steve. Starting a new conversation...\n\n"
        conversation = Conversation(
            bot_name="Steve",
            human_name=telegram_bot_membership.telegram_user.first_name
            or telegram_bot_membership.telegram_user.username,
        )
        telegram_bot_membership.telegram_user_dict = {
            k: v
            for k, v in update.message.from_user.to_dict().items()
            if not k.startswith("_")
        }
        telegram_bot_membership.save()

    # get response from conversational LLM
    text_response += conversation.prompt(update.message.text)
    # update conversation in global scope
    telegram_bot_membership_conversations[telegram_bot_membership.id] = conversation
    return text_response


def send_photo(telegram_bot_membership, local_file_path):
    # see https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#post-an-image-file-from-disk
    telegram_bot_membership.telegram_bot.send_photo(
        chat_id=telegram_bot_membership.telegram_user.effective_chat_id,
        photo=open(local_file_path, "rb"),
    )


def send_cute_puppy_photo(self, bot, chat_id, caption=""):
    doggy_response = requests.get(
        url="https://dog.ceo/api/breeds/image/random", params={}
    )
    data = doggy_response.json()
    if data.get("status") == "success" and data.get("message", "").startswith(
        "https://images.dog.ceo"
    ):
        dog_photo_url = data["message"]
        bot.send_photo(chat_id=chat_id, photo=dog_photo_url, caption=caption)
