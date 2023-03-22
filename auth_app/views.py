from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from .models import Profile
from auth_app.services import generate_code, cr_validation, create_send_activation_code, set_new_credentials
from home.services import get_user_profile


def log_out(request):
    logout(request)
    return redirect('home:home')


def check_credentials(request):
    if request.POST:
        user_profile = get_user_profile(request)
        if 'code_verify' in request.POST:
            had_set = set_new_credentials(user_profile, request.POST.get('code_verify'))
            if had_set:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})
        if 'old_email' in request.POST:
            if cr_validation('email', user_profile, request.POST.get('old_email')):
                if create_send_activation_code(user_profile, 'email', request.POST.get('new_email')) == 'exists':
                    return JsonResponse({
                        'message': 'failed'
                    })
        elif 'old_password' in request.POST:
            if cr_validation('password', user_profile, request.POST.get('old_password')):
                create_send_activation_code(user_profile, 'password', request.POST.get('new_password'))
    return render(request, 'account/settings.html')
