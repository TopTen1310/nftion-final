from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from auth_app.models import Profile
from home.models import Nft


def get_user_profile(request: WSGIRequest):
    if type(request) == User:
        profile = Profile.objects.filter(user=request).first()
    else:
        profile = get_object_or_404(Profile, user=request.user)
    return None if profile == 'AnonymousUser' else profile


def change_profile_data(request: WSGIRequest, user_profile: Profile):
    if request.POST:
        user_profile.set_user_profile_data(request.FILES.get('profile_picture'), request.POST.get('name'),
                                           request.POST.get('bio'), request.POST.get('username'))


def ordering(order_by, direction, nft_status, nft_type, deals_range, price_range, base_query):
    min_val = ''
    max_val = ''
    if order_by and order_by != 'None':
        order_by = order_by.strip()
        if direction == 'asc':
            nfts = base_query.order_by(order_by)
        elif direction == 'desc':
            nfts = base_query.order_by('-'+order_by)
        else:
            nfts = base_query.order_by(order_by)
    else:
        nfts = base_query

    replace_str = lambda x: x.replace("-", " ")
    check_status = None
    check_type = None
    if nft_status:
        nft_status = nft_status.strip()
        split_st = nft_status.split('_')
        split_st = list(map(replace_str, split_st))
        check_status = split_st
        nfts = nfts.filter(status__in=split_st)
    if nft_type:
        nft_type = nft_type.strip()
        split_type = nft_type.split('_')
        split_type = list(map(replace_str, split_type))
        check_type = split_type
        nfts = nfts.filter(nft_type__name__in=split_type)
    if deals_range:
        min_val = deals_range.split('_')[0]
        max_val = deals_range.split('_')[1]
        if max_val == 'inf':
            nfts = nfts.filter(deals_number__gte=min_val)
        elif min_val == 'inf':
            nfts = nfts.filter(deals_number__lte=max_val)
        else:
            nfts = nfts.filter(deals_number__gte=min_val, deals_number__lte=max_val)
    if price_range:
        min_val = price_range.split('_')[0]
        max_val = price_range.split('_')[1]
        if max_val == 'inf':
            nfts = nfts.filter(price__gte=min_val)
        elif min_val == 'inf':
            nfts = nfts.filter(price__lte=max_val)
        else:
            nfts = nfts.filter(price__gte=min_val, price__lte=max_val)

    return nfts, check_status, check_type, min_val, max_val
