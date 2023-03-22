from datetime import datetime, timedelta

from get_links_for_parser import get_links, start_parser, delete_scam_parser
from home.models import Nft
from nftion.celery import app


@app.task()
def start_parsing(*args, **kwargs):
    with open('collections.txt', 'r') as file:
        collections_list = file.read().split('\n')

    if 'direction' in kwargs.keys():
        print('DIRECTION IN KWARGS')
        x = -1
        while abs(x) < len(collections_list)/2:
            try:
                get_links(collections_list, x, direction=True)
            except:
                pass
            x -= 1
    else:
        get_links(collections=collections_list, col_id=0)


@app.task()
def update_existing_nft(*args, **kwargs):
    checking_list = []

    print('ТАСКА АПДЕЙТ НАЧИНАЕТСЯ', f'ВОТ КВАРГИ {kwargs}')

    nft_objects = Nft.objects.all().order_by('id')
    if 'closing_position' in kwargs.keys():

        print(f'БЫЛО ОБНАРУЖЕНО КЛОСИНГ ПОЗИШН ОТ {kwargs.get("position")} ДО {kwargs.get("closing_position")}')

        for nft in nft_objects[int(kwargs.get('position')):int(kwargs.get('closing_position'))]:
            checking_list.append(nft.get_opensea_link())

    elif 'position' in kwargs.keys() and len(kwargs.keys()) == 1:

        print(f'ОБНАРУЖЕН ОБЫЧНЫЙ ПОЗИШН')

        for nft in nft_objects[int(kwargs.get('position')):]:
            checking_list.append(nft.get_opensea_link())

    else:
        print('ПОЗИШНОВ НЕТ, ПАРШУ ВСЕ ПОДРЯД')
        for nft in nft_objects:
            checking_list.append(nft.get_opensea_link())

    start_parser(checking_list)

    return


@app.task()
def update_auto(*args, **kwargs):

    third_part = round(Nft.objects.all().count()/3)

    update_existing_nft.apply_async(
        kwargs={'position': 0, "closing_position": third_part}
    )
    update_existing_nft.apply_async(
        kwargs={'position': third_part, "closing_position": third_part*2}
    )
    update_existing_nft.apply_async(
        kwargs={'position': third_part*2}
    )


@app.task()
def update_old(*args, **kwargs):
    nft_objs = Nft.objects.filter(update_time__lt=datetime.now()-timedelta(days=1))
    objs_list = [link.get_opensea_link() for link in nft_objs]
    print(objs_list)
    start_parser(objs_list)


@app.task()
def delete_scam(*args, **kwargs):
    nfts = Nft.objects.filter(name__contains='warning')
    list_with_nft = [link.get_opensea_link() for link in nfts]

    delete_scam_parser(list_with_nft)
