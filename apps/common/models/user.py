from datetime import datetime
import hashlib

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.assistant.models.conversation_block import Author, Ilk
from apps.common.behaviors import Timestampable


class User(AbstractUser, Timestampable):
    phone_number = models.CharField(max_length=15, default="", blank=True)

    is_email_verified = models.BooleanField(default=False)
    is_beta_tester = models.BooleanField(default=False)
    is_premium_member = models.BooleanField(
        default=False
    )  # todo: create purchases or membership model for details
    agreed_to_terms_at = models.DateTimeField(null=True, blank=True)
    invited_by_user = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )

    organization_name = models.CharField(max_length=255, default="", blank=True)
    api_keys = models.JSONField(default=dict, blank=True)

    # MODEL PROPERTIES

    @property
    def author_repr(self) -> Author:
        return Author(
            id=str(self.id),
            name=self.get_full_name() or self.username,
            ilk=Ilk.HUMAN,
            handle=self.username or self.email or "",
        )

    @property
    def serialized(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_staff": self.is_staff,
            "is_active": self.is_active,
        }

    @property
    def four_digit_login_code(self):
        if self.email.endswith("@example.com"):
            return "1234"  # for test accounts
        hash_object = hashlib.md5(
            bytes(f"{self.id}{self.email}{self.last_login}", encoding="utf-8")
        )
        return str(int(hash_object.hexdigest(), 16))[-4:]

    @property
    def is_agreed_to_terms(self) -> bool:
        if self.agreed_to_terms_at and self.agreed_to_terms_at > timezone.make_aware(
            datetime(2019, 11, 1)
        ):
            return True
        return False

    @is_agreed_to_terms.setter
    def is_agreed_to_terms(self, value: bool):
        if value is True:
            self.agreed_to_terms_at = timezone.now()
        elif value is False and self.is_agreed_to_terms:
            self.agreed_to_terms_at = None

    # MODEL FUNCTIONS
    def __str__(self):
        try:
            if self.first_name:
                return self.first_name + (
                    f" {self.last_name}" if self.last_name else ""
                )
            if self.username and "@" not in self.username:
                return self.username
            if self.is_email_verified:
                return self.email.split("@")[0]
            else:
                return f"{self.email} (unverified)"
        except:
            return f"User {self.id}"
