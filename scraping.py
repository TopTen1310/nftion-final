import gc
import json
import re

from bs4 import SoupStrainer as strainer
import cchardet
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import datetime as date_time
import cloudscraper
import time

from lxml import etree
from dateutil import relativedelta
from dateutil import parser as date_parse

from collections import OrderedDict
import os
import django

from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nftion.settings")
django.setup()
from home.models import HistoryPrice


headers = {
    "accept": "application/json",
    "X-API-KEY": settings.API_KEY
}


class NftParser:

    def __init__(self, api_key, nft_link, session):
        self.API_HISTORICAL = settings.API_KEY_HISTORICAL
        self.api_key = api_key
        self.nft_link = nft_link
        self.contract_address, self.token_id = self.__set_address_token()
        self.first_sale_date = None
        self.first_price = None
        self.mint_hash = None
        self.name = None
        self.img_url = None
        self.price = None
        self.type = None
        self.status = None
        self.deals_number = None
        self.total_profit = None
        self.monthly_roi = None
        self.last_sale_date = None
        self.max_profit = None
        self.min_profit = None
        self.average_sale_duration = None
        self.average_hold_duration = None
        self.royalties = None
        self.scam = False
        self.session = session
        self.events_dict = OrderedDict()

    def __set_address_token(self):
        cropped = self.nft_link.split('/')
        return cropped[-2], cropped[-1]

    def __get_payment_token(self, event):
        return event['payment_token']['symbol']

    def scrap_opensea(self):
        """ СТатус категория роялти, цена """

        result = BeautifulSoup(requests.get(f'{self.nft_link}', verify=False, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'
        }).content, 'lxml')
        try:
            price = result.find('div', class_='Price--fiat-amount-secondary').text
            price = price.replace('$', '').replace(' ', '').replace(',', '')
            self.price = price
        except AttributeError:
            self.price = None
        price = None
        try:
            category = result.find('section', class_='item--counts')
            div_with_category = category.find_all('div')[-1]
            span_cat = div_with_category.find('span').text
            div_with_category = None
            if category is None:
                self.status = 'General'
            else:
                self.status = span_cat
        except:
            self.status = 'General'
        category = None
        trade_station_block = result.find('form', class_='TradeStation--main')
        if not trade_station_block:
            trade_station_block = result.find('div', class_='TradeStation--main')
            self.type = 'Offer available'

        self.name = result.find('section', {'class': 'item--header'}).find_all('div', recursive=False)[1].find('h1').text

        try:
            for i in result.find('section', {'class': 'item--header'}).find_all('i'):
                if i.text == 'warning':
                    self.scam = True
                    return
        except:
            pass

        result = None

        if not trade_station_block:
            self.type = 'No offers'
            return

        if trade_station_block.find_all('div', recursive=False)[-1].find('button').text == 'Buy now':
            buy_type = 'Buy now'
            self.type = buy_type

        elif len(etree.HTML(str(trade_station_block)).xpath('//button[contains(text(), "Place bid")]')) != 0:
            buy_type = 'On auction'
            self.type = buy_type

        else:
            self.type = 'Offer available'

        trade_station_block = None


    def __expand_dict_events(self, json_data):

        expand_json_data = self.session.get(f'https://api.opensea.io/api/v1/events?only_opensea=true&token_id={self.token_id}'
                                        f'&asset_contract_address={self.contract_address}&limit=200'
                                        f'&event_type=successful&cursor={json_data["next"]}', verify=False,
                                            headers=headers, stream=True)

        for raw_rs in expand_json_data.iter_lines():
            if raw_rs:
                expand_json_data = json.loads(raw_rs)

        starting_point = list(self.events_dict.keys())[-1]+1

        for event in range(len(expand_json_data['asset_events'])):
            self.events_dict.update({starting_point: expand_json_data['asset_events'][event]})
            starting_point += 1

        if expand_json_data['next']:
            self.__expand_dict_events(expand_json_data)

    def write_all_events(self):
        json_data = self.session.get(f'https://api.opensea.io/api/v1/events?only_opensea=true&token_id={self.token_id}'
                                 f'&asset_contract_address={self.contract_address}&limit=200&event_type=successful',
                                 headers=headers,verify=False, stream=True)

        for raw_rs in json_data.iter_lines():
            if raw_rs:
                json_data = json.loads(raw_rs)

        has_next = json_data['next']
        for event in range(len(json_data['asset_events'])):
            self.events_dict.update({event: json_data['asset_events'][event]})

        if has_next:
            self.__expand_dict_events(json_data)

    def set_basic_info(self):
        self.img_url = self.events_dict.get(0)['asset']['image_url']
        self.deals_number = self.events_dict.get(0)['asset']['num_sales']

    def set_first_price(self):
        self.royalties = self.__cut_decimals(self.events_dict.get(0)['asset']['asset_contract']['dev_seller_fee_basis_points'], 2)
        first_event = self.events_dict.get(list(self.events_dict.keys())[-1])

        if float(first_event['total_price']) == 0:
            first_event = self.events_dict.get(list(self.events_dict.keys())[-2])

        total_price = self.__cut_decimals(first_event['total_price'], first_event['payment_token']['decimals'])
        self.first_price = total_price

        self.first_sale_date = self._get_datetime_from_str(first_event['event_timestamp'])

    def set_last_sale_date(self) -> None:
        self.last_sale_date = self.events_dict.get(0)['event_timestamp']
        return self.last_sale_date


    def __cut_decimals(self, number, decimals):
        number = list(str(number))
        while len(number) < decimals:
            number.insert(-decimals, '0')
        number.insert(-decimals, '.')
        str_num = ''.join(number[0:5])
        if str_num[0] == '.':
            str_num = '0' + str_num

        return str_num

    def __convert_price_to_usd(self, total_price, payment_token, date):
        cut = self.__cut_decimals(total_price, payment_token['decimals'])
        historical = self.__get_historical_price(date.timestamp(), payment_token['symbol'], date)
        return float(cut)*historical

    def _get_datetime_from_str(self, date_to_convert):
        return date_parse.parse(date_to_convert)

    def set_avg_sale_duration(self):

        temp_data = 0

        temp_list_timestamps = []

        for key in self.events_dict.keys():
            try:
                temp_list_timestamps.append(self._get_datetime_from_str(self.events_dict.get(key)
                                                                        ['event_timestamp']).timestamp() -
                                            self._get_datetime_from_str(self.events_dict.get(key+1)['event_timestamp'])
                                            .timestamp())
            except TypeError:
                pass
            if self.events_dict.get(key)['listing_time']:
                temp_data += self._get_datetime_from_str(self.events_dict.get(key)['event_timestamp']).timestamp()\
                             - self._get_datetime_from_str(self.events_dict.get(key)['listing_time']).timestamp()

        finals = temp_data/len(self.events_dict.keys())

        self.average_hold_duration = self.__humanize_date(sum(temp_list_timestamps)/len(temp_list_timestamps))

        self.average_sale_duration = self.__humanize_date(finals)

    def set_max_min_profit(self):
        participants = []
        for receiver in self.events_dict.keys():
            receiver_usd = float(self.__cut_decimals(self.events_dict.get(receiver)['total_price'], self.events_dict.get(receiver)['payment_token']['decimals']))

                # self.__convert_price_to_usd(self.events_dict.get(receiver)['total_price'],
                #                                      self.events_dict.get(receiver)['payment_token'],
                #                                      date_parse.parse(self.events_dict.get(receiver)['event_timestamp']))
            for sender in self.events_dict.keys():
                if self.events_dict.get(receiver)['winner_account']['address'] == self.events_dict.get(sender)['seller']['address']\
                        and date_parse.parse(self.events_dict.get(sender)['event_timestamp']) > date_parse.parse\
                            (self.events_dict.get(receiver)['event_timestamp']):
                    sender_usd = self.__cut_decimals(self.events_dict.get(sender)['total_price'],
                                                           self.events_dict.get(sender)['payment_token']['decimals'],)
                    try:
                        if receiver_usd > 0:
                            participants.append(
                            round((float(sender_usd) - receiver_usd)/receiver_usd*100, 2)
                            )
                    except Exception as e:
                        print(e)
        if len(participants) == 0:
            self.max_profit = 'no sales'
            self.min_profit = 'no sales'
        elif len(participants) == 1:
            self.max_profit = participants[0]
            self.min_profit = participants[0]
        else:
            participants.sort()
            self.max_profit = participants[-1]
            self.min_profit = participants[0]

    def get_last_sale_price(self):
        nft_price = self.events_dict.get(0)
        nft_price = self.__cut_decimals(nft_price['total_price'], nft_price['payment_token']['decimals'])
        return nft_price

    def set_total_monthly_profit(self):
        if self.price is None:
            self.price = self.__convert_price_to_usd(self.events_dict.get(0)['total_price'],
                                                     self.events_dict.get(0)['payment_token'],
                                                     self._get_datetime_from_str(self.events_dict.get(0)['event_timestamp']))
        # print(self.get_last_sale_price(), self.first_price)
        self.total_profit = round((float(self.get_last_sale_price())/float(self.first_price))*100-100, 5)
        r = relativedelta.relativedelta(datetime.now(), self.first_sale_date)
        months_difference = (r.years * 12) + r.months
        if months_difference < 1:
            months_difference = 1
        self.monthly_roi = self.total_profit/months_difference

    def __get_historical_price(self, date_to_get, network, check_date):
        check_date = check_date.date()
        created = False
        if network == 'WETH':
            network = 'ETH'
        try:
            price = HistoryPrice.objects.get(
                ticker=network, date=check_date
            )
        except:
            price = HistoryPrice.objects.create(
                ticker=network, date=check_date, price=0
            )
            created = True
        if created:
            url = f'https://min-api.cryptocompare.com/data/pricehistorical?fsym={network}&tsyms=USD&ts={date_to_get}'
            request = requests.get(url, verify=False).json()
            price_usd = request.get(list(request.keys())[0])['USD']
            price.price = price_usd
            price.save()
            return price_usd
        else:
            return price.price

    def __humanize_date(self, seconds):
        humanized = date_time.timedelta(seconds=seconds)
        humanized = str(humanized).split(',')[0]
        humanized = humanized.split('.')[0]
        return humanized

    def set_none(self):
        self.price = None
        self.deals_number = None
        self.events_dict = None
        self.max_profit= None
        self.nft_link= None
        self.min_profit= None
        self.royalties= None
        self.monthly_roi= None
        self.img_url= None
        self.name= None
        self.first_price= None
        self.first_sale_date= None
        self.last_sale_date= None
        self.type= None
        self.status= None
        self.contract_address= None
        self.token_id= None
        self.average_sale_duration= None
        self.average_hold_duration= None
        self.mint_hash= None

    def get_info(self):
        self.scrap_opensea()
        if self.scam:
            return False
        self.write_all_events()
        self.set_basic_info()
        self.set_first_price()
        self.set_last_sale_date()
        self.set_total_monthly_profit()
        self.set_avg_sale_duration()
        self.set_max_min_profit()

        full_dict = {
            'price': self.price,
            'img_link': self.img_url,
            'name': self.name,
            'type': self.type,
            'category': self.status,
            'total_profit': self.total_profit,
            'monthly_roi': self.monthly_roi,
            'deals_number': self.deals_number,
            'last_sale_date': self.last_sale_date,
            'max_profit_per_sale': self.max_profit,
            'min_profit_per_sale': self.min_profit,
            'average_sale_duration': self.average_sale_duration,
            'average_hold_duration': self.average_hold_duration,
            'royalty': self.royalties,
            'buy_link': self.nft_link,
            'opensea_link': self.nft_link
        }

        self.set_none()
        return full_dict

    def get_scam(self):
        self.scrap_opensea()
        if self.scam:
            return True
