from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm)
from django.contrib.auth.models import Permission
from django.db.models import Q
from cards.models import NFCCard

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data["role"]
        if role == "superuser":
            user.is_staff = True
            user.is_superuser = True
            user.save()

        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            match = User.objects.filter(email=email)
            if match:
                raise forms.ValidationError("This email address is already in use")
            return email


class CustomUserChangeForm(UserChangeForm):

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data["role"]
        if role == "superuser":
            user.is_staff = True
            user.is_superuser = True
            user.save()

        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            match = User.objects.filter(email=email).exclude(id=self.instance.pk)
            if match:
                raise forms.ValidationError("This email address is already in use")
            return email


class UserDetailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            match = User.objects.filter(email=email).exclude(id=self.instance.pk)
            if match:
                raise forms.ValidationError("This email address is already in use")
            return email


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "User Name Or Email"})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                try:
                    user = User.objects.get(
                        Q(username__iexact=username) | Q(email__iexact=username)
                    )
                except User.DoesNotExist:
                    user = None
                if user is not None:
                    if not user.is_active:
                        self.confirm_login_allowed(user)
                    else:
                        raise self.get_invalid_login_error()
                else:
                    raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            error = "The account is closed, please contact us for more details."
            raise forms.ValidationError(error)


class RegisterForm(UserCreationForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if email:
            match = User.objects.filter(email=email)
            if match:
                raise forms.ValidationError("This email address is already in use")
            return email

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["email"].required = True

    class Meta:
        model = User
        fields = ("email", "username")
