from apps.common.models import User
from apps.integration.loops.client import LoopsClient


def send_password_reset_email(user: User, reset_url: str):
    """
    Send a password reset email

    :param User user: common.User object
    :param str reset_url: The URL to redirect the user to reset their password
    """
    loops_client = LoopsClient()
    loops_client.transactional_email(
        to_email=user.email,
        transactional_id="__loops_email_id__",
        data_variables={
            "passwordresetlink": reset_url,
        },
    )
