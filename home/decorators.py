from functools import wraps

from django.http import HttpResponseRedirect
from django.urls import reverse

from home.services import get_user_profile


def verified_account_required(function=None):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        user_profile = get_user_profile(request)
        if not user_profile.get_profile_status():
            return HttpResponseRedirect(reverse('home:need_confirm'))
        return function(request, *args, **kwargs)
    return wrap
