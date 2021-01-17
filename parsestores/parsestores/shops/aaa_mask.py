import math
import re
from pprint import pprint


def get_item_fieldnames():
    return ['id', 'name', 'category',
            'category_1', 'category_2', 'price',
            'old_price', 'price_iso_code', 'brand',
            'gender', 'site_name']


def get_urls_gender_categories():
    return {
        'men': {
            'Одежда': '',
            'Обувь': '',
            'Bags': '',
            'Аксессуары': '',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': '',
            'Обувь': '',
            'Bags': '',
            'Аксессуары': '',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Девочки': '',
            'Мальчики': '',
            'Аксессуары': ''
        }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    for tag in tree.xpath(''): # <<-- Category level 1
        href = tag.get('href')      # <<--href from tag
        title = tag.text            # <<--title from tag

        if href is None or title is None or not href or not title:
            continue

        result.append((href, title))  # <<--value list or str

    return result


def find_cat2_with_title(tree, response_url):
    result = []

    for tag in tree.xpath(''):
        href = tag.get('href')  # <<--href from tag
        title = tag.text        # <<--title from tag

        if href is None or title is None or not href or not title:
            continue

        result.append((href, title))  # <<--value list or str

    return result


def get_items_data(tree):
    fieldnames = get_item_fieldnames()

    results = []

    product_blocks = tree.xpath('') # <-- PRODUCT BLOCKS
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
        if not item['price']:
            item['price'] = _get_current_price(block)

        # Old_price
        item['old_price'] = _get_old_price(block)

        # Price ICO Code
        item['price_iso_code'] = _get_price_iso_code(block)

        # Site name
        item['site_name'] = _get_site_name('block')

        if not item['id'] or not item['brand'] or not item['price']:
            continue

        results.append(item)

    return results


def _get_id(block):
    try:
        return block.xpath('')[0] # <<-- xpath to ID
    except:
        return ''


def _get_name(block):
    try:
        return block.xpath('')[0].strip() # <<-- xpath to NAME
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('')[0].strip() # <<-- xpath to BRAND
    except:
        return ''


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9]').findall(price)))  # <<-- CHECK REG for symbols
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(block.xpath('')[0]) # <<-- xpath to PRICE
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(block.xpath('')[0]) # <<-- xpath to ALTERNATIVE PRICE
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(block.xpath('')[0]) # <<-- xpath to OLD PRICE
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('')[0].strip() # <<-- xpath to ISO CODE
    except:
        return 'RUB'


def _get_site_name(block):
    return ""


def get_pagination_urls(tree, response_url):
    result = []
    max_pag_number = _get_max_pagination_number(tree)

    if max_pag_number != 1:
        for pag in range(2, max_pag_number + 1):
            result.append(f'{response_url}?page={pag}')  # <<-- pagination param

    return result


def _get_max_pagination_number(tree):
    max_num = 1
    pag_text = tree.xpath('') # <<-- xpath to PAGINATION TEXT
    for pag_t in pag_text:
        try:
            pag_n = int(''.join(re.compile('[0-9]').findall(pag_t)))
            if pag_n > max_num:
                max_num = pag_n
        except:
            continue
    return max_num
