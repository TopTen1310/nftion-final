from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from auth_app.forms import ProfileForm, SupportForm
from .services import get_user_profile, change_profile_data, ordering
from .models import Nft, SupportAppeal, NftType

from .decorators import verified_account_required


# Create your views here.
def home(request):
    # if not request.user.is_authenticated:
    # 	context = {'a':'a'}
    # 	response = render(request, 'base.html', context)
    # 	return response
    # else:
    context = {'a': 'a'}
    return render(request, 'base.html', context)
    
def error_404(request):
    context = {'a': 'a'}
    return render(request, 'errors/404.html', context)
    


@login_required
@verified_account_required
def dashboard(request):
    """ Main page with table filled with nft """
    order_by = str(request.GET.get('order_by')).replace(' ', '')
    direction = str(request.GET.get('direction')).replace(' ', '')
    order_by = None if order_by == 'None' else order_by
    direction = None if direction == 'None' else direction
    deals_range = request.GET.get('deals_range')
    deals_range = deals_range.replace(' ', '') if deals_range else deals_range
    price_range = request.GET.get('price_range')
    price_range = price_range.replace(' ', '') if price_range else price_range
    nft_status = request.GET.get('nft_status')
    nft_type = request.GET.get('nft_type')

    nfts, check_status, check_type, min_val, max_val = ordering(order_by, direction, nft_status, nft_type, deals_range, price_range, Nft.objects.all())
    buy_now = None
    on_auction = None
    if Nft.objects.all().filter(status='Buy now').count() > 0:
        buy_now = True
    if Nft.objects.all().filter(status='On auction').count() > 0:
        on_auction = True

    total_nft = nfts.count()
    paginator = Paginator(nfts, 14)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    wishlist = get_user_profile(request).get_wishlist_nft()
    statuses = NftType.objects.all()
    context = {'user_profile': get_user_profile(request), 'nfts': nfts, 'order_by': order_by, 'direction':direction, 'page_obj': page_obj,
               'total_nft_count': total_nft, 'price_range': price_range, 'deals_range': deals_range, 'min_value': min_val, 'max_value': max_val,
               'nft_status': nft_status, 'nft_type': nft_type, 'check_status': check_status, 'check_type': check_type,
               'wishlist': wishlist, 'statuses': statuses, 'buy_now': buy_now, 'on_auction': on_auction
               }
    return render(request, 'dashboard.html', context)


@login_required
@verified_account_required
def add_to_favorite(request, nft_id):
    nft = get_object_or_404(Nft, id=nft_id)
    user_profile = get_user_profile(request)
    if nft in user_profile.get_wishlist_nft():
        return JsonResponse({'success': False})
    user_profile.add_to_wishlist_nft(nft)
    return JsonResponse({'success': True })


@login_required
@verified_account_required
def remove_from_favorite(request, nft_id):
    get_user_profile(request).remove_from_wishlist(get_object_or_404(Nft, id=nft_id))
    return JsonResponse({'success': True})


# @login_required
def privacy_policy(request):
    context={"title":"Privacy Policy"}
    return render(request, 'account/privacy_policy.html', context)
    
# @login_required
def terms_conditions(request):
    context={"title":"Terms & Conditions"}
    return render(request, 'account/terms.html', context)
    
    
    

@login_required
@verified_account_required
def settings(request):
    context = {'user_profile': get_user_profile(request)}
    return render(request, 'account/settings.html', context)


@login_required
@verified_account_required
@csrf_exempt
def profile(request):
    """ User's profile page """
    user_profile = get_user_profile(request)
    if request.method == 'POST':
        POST = request.POST.copy()
        POST['email'] = user_profile.get_email()
        form = ProfileForm(POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            if form.check_coincidence(cleaned_data['username'], user_profile):
                user_profile.set_user_profile_data(avatar=cleaned_data['avatar'], name=cleaned_data['name'],
                                                   bio=cleaned_data['bio'], username=cleaned_data['username'])
                return HttpResponseRedirect(reverse('home:dashboard'))
            else:
                return JsonResponse({'username_taken': True})
    else:
        form = ProfileForm(initial={'email': user_profile.get_email(), 'name': user_profile.name,
                                    'username': user_profile.user.username, 'bio': user_profile.bio})

    context = {'user_profile': user_profile, 'form': form}
    return render(request, 'account/profile.html', context)


@login_required
@verified_account_required
def update_profile(request):
    user_profile = get_user_profile(request)
    change_profile_data(request, user_profile)
    return redirect('home:profile')


@login_required
@verified_account_required
def favorites(request):
    """ Page of favorites nft of user """
    user_profile = get_user_profile(request)
    order_by = str(request.GET.get('order_by')).replace(' ', '')
    direction = str(request.GET.get('direction')).replace(' ', '')
    order_by = None if order_by == 'None' else order_by
    direction = None if direction == 'None' else direction
    deals_range = request.GET.get('deals_range')
    deals_range = deals_range.replace(' ', '') if deals_range else deals_range
    price_range = request.GET.get('price_range')
    price_range = price_range.replace(' ', '') if price_range else price_range
    nft_status = request.GET.get('nft_status')
    nft_type = request.GET.get('nft_type')

    nfts, check_status, check_type, min_val, max_val = ordering(order_by, direction, nft_status, nft_type, deals_range, price_range, user_profile.get_wishlist_nft())

    buy_now = None
    on_auction = None
    if user_profile.get_wishlist_nft().filter(status='Buy now').count() > 0:
        buy_now = True
    if user_profile.get_wishlist_nft().filter(status='On auction').count() > 0:
        on_auction = True

    total_nft = nfts.count()
    paginator = Paginator(nfts, 14)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    statuses = NftType.objects.all()
    context = {'user_profile': user_profile, 'nfts': nfts, 'order_by': order_by,'statuses': statuses,
               'price_range': price_range, 'deals_range': deals_range, 'min_value': min_val, 'max_value': max_val,
               'nft_status': nft_status, 'nft_type': nft_type, 'check_status': check_status, 'check_type': check_type,
               'direction':direction,'page_obj': page_obj,'total_nft_count': total_nft,
               'buy_now': buy_now, 'on_auction': on_auction
               }
    return render(request, 'account/favorite.html', context)


@login_required
@verified_account_required
def support(request):
    user_profile = get_user_profile(request)
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            SupportAppeal.objects.create(
                sender=user_profile,
                first_name=cleaned_data['first_name'],
                last_name=cleaned_data['last_name'],
                email=cleaned_data['email'],
                phone_number=cleaned_data['phone_number'],
                appeal_body=cleaned_data['appeal_body'],
            )
            return JsonResponse({
                'success': True
            })
        #     return HttpResponseRedirect(reverse('home:dashboard'))
        # else:
        #     return HttpResponseRedirect(reverse('home:support'))
    else:
        form = SupportForm(initial={'email': user_profile.get_email()})
    context = {'user_profile': user_profile, 'form': form}
    return render(request, 'account/support.html', context)


# def need_confirm(request):
#     return render(request, '')

def handler500(request, *args, **argv):
    return render(request, 'errors/505.html', status=500)


def handler400(request, *args, **argv):
    return render(request, 'errors/400.html', status=400)


def handler401(request, *args, **argv):
    return render(request, 'errors/401.html', status=401)


def handler404(request, *args, **argv):
    return render(request, 'errors/404.html', status=404)
