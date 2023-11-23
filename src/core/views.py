from axes.utils import reset
from ipware.ip import get_client_ip

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import AxesCaptchaForm


def locked_out(request):
    if request.POST:
        form = AxesCaptchaForm(request.POST)
        if form.is_valid():
            ip, is_routable = get_client_ip(request)
            reset(ip=ip)
            return HttpResponseRedirect(reverse_lazy('cas_login'))
    else:
        messages.error(
            request,
            _(
                'Too many failed login attempts. '
                'Please enter the letters in the box beneath.'
            ),
        )
        form = AxesCaptchaForm()

    return render(request, 'core/locked_out.html', dict(form=form))
