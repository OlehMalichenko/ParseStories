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
            'Одежда': 'https://www.quiksilver.ru/mens-odezhda/',
            'Обувь и Аксессуары': 'https://www.quiksilver.ru/mens-aksessuary/',
            'Bags': '',
            'Аксессуары': '',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': 'https://www.quiksilver.ru/women-odezhda/',
            'Обувь': '',
            'Bags': '',
            'Аксессуары': '',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Одежда': 'https://www.quiksilver.ru/kids-odezhda/',
            'Обувь и Аксессуары': 'https://www.quiksilver.ru/kids-aksessuary/',
            'Аксессуары': ''
        }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    for tag in tree.xpath('//li[@class="expandable active"]'
                          '//li[contains(@id, "ref_cat_")]'
                          '/a'):
        href = tag.get('href')  # href from tag
        title = tag.get('title')  # title from tag

        if href is None or title is None or not href or not title:
            continue

        result.append((href, title))  # !!! value list or str !!!

    return result


def find_cat2_with_title(tree, response_url):
    result = []

    for tag in tree.xpath('//div[@class="category-item__name active"]'
                          '/following-sibling::div[@class="categories-list categories-list__sub-menu"]'
                          '//div[@class="category-item__name"]'):
        data_test = tag.get('data-test')  # href from tag
        title = tag.xpath('./span/text()')  # title from tag

        if data_test is None or title is None or not data_test or not title:
            continue

        result.append((f'{response_url}/{data_test}', title[0]))  # !!! value list or str !!!

    return result


def get_items_data(tree):
    fieldnames = get_item_fieldnames()

    results = []

    product_blocks = tree.xpath('//div[@class="isproductgrid"]/div[contains(@class, "product")]')
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
        if item['price'] == 0.0:
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
        return block.xpath('.//div[@data-productid]/@data-productid')[0]
    except:
        return ''


def _get_name(block):
    try:
        return block.xpath('.//a[@class="omni_search_link product_search_hit_tile_product_Link"]/@title')[0]
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
    except:
        return 'Quiksilver'


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9\\.]').findall(price)))
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="price data-price"]/@data-salesprice')[0])
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="price data-price"]/@data-standardprice')[0])
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="price data-price"]/@data-salesprice')[0])
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('//div[@class="countries__selected"]'
                          '/span[@class="countries__item-values"]/text()')[0].strip()
    except:
        return 'RUB'


def _get_site_name(block):
    return "Quiksilver.ru"


def get_pagination_urls(tree, response_url):
    try:
        return tree.xpath('//a[@class="pagenext"]/@href')[0]
    except:
        return ''



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
