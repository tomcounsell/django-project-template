from datetime import datetime

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from apps.public.views.main_content_view import MainContentView

INVITE_CODES = {"cmhat", "steve"}


from django import forms


class AccountCreateForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True
    )
    invite_code = forms.CharField(label="Invite Code", required=False)


class LoginView(auth_views.LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True


# Assuming AbstractUser is being used directly
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = AbstractUser
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "Friedrich", "class": "input"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Hayak", "class": "input"}
            ),
            "email": forms.EmailInput(attrs={"disabled": True, "class": "input"}),
        }


class SettingsView(LoginRequiredMixin, MainContentView):
    template_name = "account/settings.html"
    # url = "/account/settings/"

    def get(self, request, *args, **kwargs):
        if "user_form" not in self.context:
            self.context["user_form"] = UserSettingsForm(instance=request.user)
        if "password_form" not in self.context:
            self.context["password_form"] = auth_views.PasswordChangeForm(
                user=request.user
            )
        return self.render()

    def post(self, request, *args, **kwargs):
        if "first_name" in request.POST:
            self.context["user_form"] = UserSettingsForm(
                request.POST, instance=request.user
            )
            if self.context["user_form"].is_valid():
                self.context["user_form"].save()
                messages.success(request, "User settings updated.")
        else:
            self.context["password_form"] = auth_views.PasswordChangeForm(
                request.user, request.POST
            )
            if self.context["password_form"].is_valid():
                self.context["password_form"].save()
                update_session_auth_hash(request, self.context["password_form"].user)
                messages.success(request, "Password updated.")
            else:
                messages.error(
                    request,
                    f"Password not updated.",
                )

        return self.get(request, *args, **kwargs)


class HomeView(LoginRequiredMixin, MainContentView):
    template_name = "pages/home.html"
    # url = "/"  #  root of host
