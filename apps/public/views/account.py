from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractUser
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.common.models import User
from apps.item.models import Brand
from apps.public.views.main_content_view import MainContentView

INVITE_CODES = {"cmhat", "steve"}


from django import forms


class AccountCreateForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True
    )
    brand_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    brand_description = forms.CharField(widget=forms.HiddenInput(), required=False)
    invite_code = forms.CharField(label="Invite Code", required=False)


class AccountCreateView(View):
    http_method_names = ["get", "post"]

    def get(self, request, *args, **kwargs):
        return render(
            request,
            template_name="pages/onboarding.html",
            context={"component_name": "onboarding_signup"},
        )

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            brand_name = form.cleaned_data["brand_name"] or "new brand"
            brand_description = form.cleaned_data["brand_description"]
            invite_code = form.cleaned_data["invite_code"]

            if existing_user := User.objects.filter(username=email).first():
                if not existing_user.is_active:
                    # this email may have been blocked
                    messages.error(request, "problem with your account")
                    return redirect("public:account-login")
                # authenticate email and password
                if existing_user.check_password(password):
                    login(request, existing_user)
                    return redirect("public:home")
                else:
                    messages.error(
                        request,
                        "Account already exists. Please login with your previously set password.",
                    )
                return redirect("public:account-login")

            elif invite_code.lower() not in INVITE_CODES:
                messages.error(request, "Invalid invite code.")
                return redirect("public:account-create")

            user = User.objects.create(email=email, username=email)
            user.set_password(password)
            if datetime.now() < datetime(2024, 1, 1):
                user.is_beta_tester = True
                user.invited_by_user = User.objects.get(email="tom@yuda.me")
            user.is_active = True
            user.save()
            # authenticate login
            login(request, user)

            brand = Brand.objects.create(name=brand_name, author=user)
            if brand_description:
                brand.assets.create(name="description", content=brand_description)
            return redirect("public:home")


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


class SurveyForm(forms.Form):
    agree_to_terms = forms.BooleanField(required=True)


class HomeView(LoginRequiredMixin, MainContentView):
    template_name = "pages/home.html"
    # url = "/"  #  root of host

    def get(self, request, *args, **kwargs):
        self.context = {}

        # REASONS why they can't use the app yet

        if not request.user.is_agreed_to_terms:
            self.context["component_name"] = "survey"
            return render(request, self.template_name, self.context)

        # elif not request.user.is_email_verified:
        #     messages.error(request, "Please verify your email.")
        #     return render(request, self.template_name, self.context)

        brand = request.user.brands.first()
        return redirect("public:brand", brand_id=brand.id, brand_slug=brand.slug)

    def post(self, request, *args, **kwargs):
        survey_form = SurveyForm(request.POST)
        if survey_form.is_valid():
            if survey_form.cleaned_data["agree_to_terms"]:
                request.user.agreed_to_terms_at = timezone.now()
                request.user.save()

        return self.get(request, *args, **kwargs)
