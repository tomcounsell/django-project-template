from telegram import Message
from apps.communication.telegram.commands.decorator import telegram_command
from apps.communication.telegram.commands import start, random_dog
from apps.communication.telegram.commands import help, info


# DEFAULT COMMANDS #
@telegram_command("hello", response_type="text")
def hello(telegram_bot_membership, message: Message, context):
    return f"hello, {message.from_user.first_name}"


@telegram_command("echo")
def echo(telegram_bot_membership, message: Message, context):
    return "Thanks for the args: \n\n" + "\n".join(context.args)


@telegram_command("expectations", response_type="text")
def expectations(telegram_bot_membership, message: Message, context):
    return "Expecting the following: " + ",".join(
        telegram_bot_membership.expectations_list
    )


# UNKNOWN COMMAND - CATCHES ALL ELSE
def unknown_command(update, context):
    """Unknown command"""
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Sorry, I didn't understand that command."
    )


standard_commands = [
    start.start,
    help.help_command_list,
    info.info,
]

feature_commands = [
    random_dog.random_dog,
]

public_commands = standard_commands + feature_commands

commands = (
    standard_commands
    + feature_commands
    + [
        # TEST EXAMPLE COMMANDS
        hello,
        expectations,
        echo,
    ]
)

expectation_handlers = {
    # "photo_for_dog_breed": dog_breeds.handle_photo_upload,
}
