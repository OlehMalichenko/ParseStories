import math
import re
from pprint import pprint

import demjson


def get_item_fieldnames():
    return ['id', 'name', 'category',
            'category_1', 'category_2', 'price',
            'old_price', 'price_iso_code', 'brand',
            'gender', 'site_name']


def get_urls_gender_categories():
    return {
        'men': {
            'Одежда': 'https://newbalance.ru/catalog/men/odezhda/?SHOWALL_1=1',
            'Обувь': 'https://newbalance.ru/catalog/men/man_shoes/?SHOWALL_1=1',
            'Bags': '',
            'Аксессуары': 'https://newbalance.ru/catalog/women/women_aksessuary/?SHOWALL_1=1',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': 'https://newbalance.ru/catalog/women/women_clothes/?SHOWALL_1=1',
            'Обувь': 'https://newbalance.ru/catalog/women/women_shoes/?SHOWALL_1=1',
            'Bags': '',
            'Аксессуары': 'https://newbalance.ru/catalog/women/women_aksessuary/?SHOWALL_1=1',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Обувь для мальчиков': 'https://newbalance.ru/catalog/kids/boys_shoes/?SHOWALL_1=1',
            'Обувь для девочек': 'https://newbalance.ru/catalog/kids/girls_shoes/?SHOWALL_1=1',
            'Малыши': 'https://newbalance.ru/catalog/kids/malyshi/?SHOWALL_1=1',
            'Аксессуары': 'https://newbalance.ru/catalog/kids/accessories_child/?SHOWALL_1=1'
        }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    for tag in tree.xpath('//div[contains(@data-auto-id, "ТИП ТОВАРА")]'
                          '//a[@class="filter___1GysO"]'):
        href = tag.get('href')  # href from tag
        title = tag.xpath('.//input[@class="gl-checkbox__input"]/@title')  # title from tag

        if href is None or title is None or not href or not title:
            continue

        result.append((href, title[0]))  # !!! value list or str !!!

    return result


def find_cat2_with_title(tree, response_url):
    result = []

    for tag in tree.xpath('//div[contains(@data-auto-id, "ВИД СПОРТА")]'
                          '//a[@class="filter___1GysO"]'):
        href = tag.get('href')  # href from tag
        title = tag.xpath('.//input[@class="gl-checkbox__input"]/@title')  # title from tag

        if href is None or title is None or not href or not title:
            continue

        result.append((href, title[0]))  # !!! value list or str !!!

    return result


def get_items_data(tree):
    fieldnames = get_item_fieldnames()

    results = []

    product_blocks = get_script_data(tree)
    # print(len(product_blocks))

    for block in product_blocks:
        item = dict.fromkeys(fieldnames)
        # ID
        item['id'] = _get_id(block)

        # Name
        item['name'] = _get_name(block)

        # Brand
        item['brand'] = _get_brand(block)

        # Price
        item['price'] = _get_price(block)
        # if not item['price']:
        # 	item['price'] = _get_current_price(block)

        # Old_price
        item['old_price'] = _get_old_price(block)

        # Price ICO Code
        item['price_iso_code'] = _get_price_iso_code(block)

        # Site name
        item['site_name'] = _get_site_name(block)

        item['category'], item['category_1'], item['category_2'] = get_categories(block)

        if not item['id'] or not item['brand'] or not item['price'] or not item['category'] or not item['category_1'] or not item['category_2']:
            continue

        results.append(item)

    return results


def get_script_data(tree):
    try:
        script_text = tree.xpath('//script[contains(text(), "window.digitalData =")]/text()')[0]
        script_text = script_text.split('window.digitalData =')[1].strip()
        all_data =  demjson.decode(script_text)
        return all_data['listing']['items']
    except:
        return []



def _get_id(block):
    try:
        return block['skuCode']
    except:
        return ''


def _get_name(block):
    try:
        return block['name']
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
    except:
        return 'New Balance'


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9]').findall(price)))
    except:
        return 0.0


def _get_price(block):
    try:
        return float(block['unitSalePrice'])
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(
            block.xpath('.//div[@class="gl-price-item gl-price-item--small notranslate"]/text()')[0])
    except:
        return 0.0


def _get_old_price(block):
    try:
        return float(block['unitPrice'])
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('//div[@class="countries__selected"]'
                          '/span[@class="countries__item-values"]/text()')[0].strip()
    except:
        return 'RUB'


def _get_site_name(block):
    return "NewBalance.ru"


def get_categories(block):
    category = ''
    category_1 = ''
    category_2 = ''

    try:
        cat_list = block['category']
        if len(cat_list) > 1:
            category = '/'.join(cat_list)
            category_1 = cat_list[1]
            if len(cat_list) > 2:
                category_2 = cat_list[2]
            else:
                category_2 = category_1

    except:
        return '' * 3

    return category, category_1, category_2


def get_pagination_urls(tree, response_url):
    result = []
    max_pag_number = _get_max_pagination_number(tree)

    if max_pag_number != 1:
        for pag in range(2, max_pag_number + 1):
            result.append(f'{response_url}?page={pag}')

    return result


def _get_max_pagination_number(tree):
    max_num = 1
    pag_text = tree.xpath('//a[@class="gizmo-pagination__link"]/text()')
    for pag_t in pag_text:
        try:
            pag_n = int(''.join(re.compile('[0-9]').findall(pag_t)))
            if pag_n > max_num:
                max_num = pag_n
        except:
            continue
    return max_num
