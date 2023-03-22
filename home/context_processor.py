from .services import get_user_profile


def get_user_profile_e(request):
    try:
        profile = get_user_profile(request)
    except:
        profile = ''
    return {
       'us_profile': profile,
    }