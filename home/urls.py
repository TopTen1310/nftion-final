from django.urls import path, include
from . import views
from nftion import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('favorites/', views.favorites, name='favorites'),
    path('settings/', views.settings, name='settings'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('support/', views.support, name='support'),
    path('404/', views.error_404, name='error_404'),
    
    # path('need-confirm/', views.need_confirm, name='need_confirm'),
    path('dashboard/add_to_favorite/<int:nft_id>', views.add_to_favorite, name='add_to_favorite'),
    path('favorites/remove_from_favorite/<int:nft_id>', views.remove_from_favorite, name='remove_from_favorite')
]


# if settings.DEBUG == False:
# 	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# elif settings.DEBUG == True:
# 	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
	