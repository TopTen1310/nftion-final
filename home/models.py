from datetime import datetime

from django.db import models


class Nft(models.Model):
    """ Model for parser """
    name = models.CharField(max_length=255, verbose_name='Nft name')
    img_link = models.CharField(max_length=255, verbose_name='Link to nft image')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Nft price")
    nft_type = models.ForeignKey('home.NftType', on_delete=models.CASCADE, verbose_name='Type of nft', related_name='nft_type')
    status = models.CharField(max_length=155)
    total_profit = models.DecimalField(max_digits=14, decimal_places=2)
    opensea_link = models.CharField(max_length=255, unique=True)
    deals_number = models.IntegerField()
    monthly_roi = models.DecimalField(max_digits=14, decimal_places=2)
    # last_sale -> event_timestamp if event type successful
    last_sale_date = models.DateTimeField()
    max_profit_per_sale = models.DecimalField(max_digits=14, decimal_places=2)
    min_profit_sale = models.DecimalField(max_digits=14, decimal_places=2)
    average_sale_duration = models.CharField(max_length=355, null=True)
    average_hold_duration = models.CharField(max_length=355, null=True)
    # fees -> seller fees
    royalty = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Royalty percent')

    buy_link = models.CharField(max_length=255, verbose_name='Link to buy nft')

    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_opensea_link(self):
        return self.opensea_link


class NftType(models.Model):
    """ Types of Nft model """
    name = models.CharField(max_length=255, verbose_name='Type name')

    def __str__(self):
        return self.name


class HistoryPrice(models.Model):
    """ Model for storing historical price of tickers """
    ticker = models.CharField(max_length=155)
    price = models.FloatField(null=True, blank=True)
    date = models.DateField(auto_now_add=False, null=True, blank=True)

    class Meta:
        unique_together = ('ticker', 'date')

    def __str__(self):
        return ''.join(str(self.date.isoformat()))


class SupportAppeal(models.Model):
    """ Model for support form """
    sender = models.ForeignKey('auth_app.Profile', on_delete=models.CASCADE, verbose_name='Sender')
    first_name = models.CharField(max_length=255, verbose_name="Sender's first name")
    last_name = models.CharField(max_length=255, verbose_name="Sender's last name")
    email = models.EmailField(max_length=255, verbose_name="Sender's email")
    phone_number = models.CharField(max_length=75, null=True, blank=True, verbose_name="Sender's phone number")
    appeal_body = models.TextField(max_length=5000, verbose_name="Sender's appeal")

    def __str__(self):
        return f'Appeal №{self.id}, from {self.sender}'
