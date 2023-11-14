from captcha.fields import CaptchaField
from mama_cas.forms import LoginForm as MamaCasLoginForm

from django import forms
from django.utils.translation import gettext_lazy as _


class AxesCaptchaForm(forms.Form):
    captcha = CaptchaField()


# TODO remove as soon as this is fixed in MamaCAS
class LoginForm(MamaCasLoginForm):
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput,
        strip=False,
        error_messages={'required': _('Please enter your password')},
    )
