import random

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from auth_app.models import ActivationCode
from nftion import settings


def generate_code():
    return ''.join(random.choices('0123456789', k=4))


def cr_validation(cred_type, user_profile, cred_info):
    if cred_type == 'email':
        if user_profile.user.email == cred_info:
            return True
        return False
    elif cred_type == 'password':
        return user_profile.user.check_password(cred_info)


def create_send_activation_code(user_profile, action, new_data):
    code = generate_code()
    for exp_code in ActivationCode.objects.filter(user=user_profile, action=action):
        exp_code.set_expired()
    user_model = get_user_model()
    if user_model.objects.filter(email=new_data).exists():
        return 'exists'
    ActivationCode.objects.create(user=user_profile, confirmation_code=code, action=action, change_to=new_data)
    send_mail(
        'Confirmation code',
        f'Your confirmation code is {code}', settings.EMAIL_HOST_USER, [user_profile.user.email],
        fail_silently=settings.FAIL_SILENTLY_EMAIL)


def set_new_credentials(user_profile, code):
    act_code = ActivationCode.objects.filter(user=user_profile, expired=False, confirmation_code=code)
    if act_code.exists():
        if act_code.first().action == 'email':
            user_profile.user.email = act_code.first().change_to
            EmailAddress.objects.create(
                user=user_profile.user, email=act_code.first().change_to, verified=True, primary=True
            )
        else:
            user_profile.user.set_password(act_code.first().change_to)
        user_profile.user.save()
        act_code.first().set_expired()
        return True
    return False
