from django.contrib import admin
from .models import Nft, NftType, SupportAppeal, HistoryPrice


class NftAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'total_profit', 'update_time')
    search_fields = ('name', 'status', 'price', 'total_profit')


admin.site.register(Nft, NftAdmin)

admin.site.register(NftType)

admin.site.register(SupportAppeal)


class HistoryPriceAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'date', 'price')


admin.site.register(HistoryPrice, HistoryPriceAdmin)
