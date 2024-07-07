from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
    UsernameField,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Booking, Customer
from decimal import Decimal


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-lg", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Password Confirmation",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        )
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                "placeholder": "Password",
            }
        ),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New Password"}
        ),
        label="New Password",
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm New Password"}
        ),
        label="Confirm New Password",
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Old Password"}
        ),
        label="Old Password",
    )
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "New Password"}
        ),
        label="New Password",
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm New Password"}
        ),
        label="Confirm New Password",
    )


class BookingForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15)
    customer_name = forms.CharField(max_length=100)

    class Meta:
        model = Booking
        fields = [
            "appointment_datetime",
            "number_of_appointments",
            "artist",
            "package",
            "advance_payment",
            "payment_method",
            "discount_percentage",
        ]

    def clean(self):
        cleaned_data = super().clean()
        package = cleaned_data.get("package")
        advance_payment = cleaned_data.get("advance_payment")
        discount_percentage = cleaned_data.get("discount_percentage")

        if package and advance_payment is not None and discount_percentage is not None:
            package_price = package.price
            discount_amount = package_price * (
                Decimal(discount_percentage) / Decimal("100")
            )
            net_amount = package_price - discount_amount
            total_amount = net_amount
            balance_amount = total_amount - Decimal(advance_payment)

            cleaned_data["balance_amount"] = balance_amount
            cleaned_data["total_payment"] = total_amount

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        phone_number = self.cleaned_data["phone_number"]
        customer_name = self.cleaned_data["customer_name"]

        customer, created = Customer.objects.get_or_create(
            phone_number=phone_number, defaults={"name": customer_name}
        )

        instance.customer = customer
        instance.balance_amount = self.cleaned_data["balance_amount"]
        instance.total_payment = self.cleaned_data["total_payment"]

        if commit:
            instance.save()
        return instance
