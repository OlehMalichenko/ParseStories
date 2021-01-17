import math
import re
from pprint import pprint

# !!!!!!!!!!!!!!!!!!!!!! Не видно цены. Нужен Селениум !!!!!!!!!!!!!!!!!!!!!!!!!!

def get_item_fieldnames():
    return ['id', 'name', 'category',
            'category_1', 'category_2', 'price',
            'old_price', 'price_iso_code', 'brand',
            'gender', 'site_name']


def get_urls_gender_categories():
    return {
        'men': {
            'Одежда': 'https://www.adidas.ru/muzhchiny-odezhda',
            'Обувь': 'https://www.adidas.ru/muzhchiny-obuv',
            'Bags': '',
            'Аксессуары': 'https://www.adidas.ru/muzhchiny-aksessuary',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': 'https://www.adidas.ru/zhenshchiny-odezhda',
            'Обувь': 'https://www.adidas.ru/zhenshchiny-obuv',
            'Bags': '',
            'Аксессуары': 'https://www.adidas.ru/zhenshchiny-aksessuary',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Подростки': 'https://www.adidas.ru/deti-podrostki_8_16_let',
            'Дети': 'https://www.adidas.ru/deti-deti_4_8_let',
            'Малыши': 'https://www.adidas.ru/deti-malyshi_1_4_goda%7Cnovorozhdennye_0_1_goda'
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

    product_blocks = tree.xpath('//div[@class="grid-item___3rAkS"]')
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
        item['site_name'] = _get_site_name(block)

        # if not item['id'] or not item['brand'] or not item['price']:
        #     continue

        results.append(item)

    return results


def _get_id(block):
    try:
        data_id = block.get('data-grid-id')
        return data_id if data_id is not None else ''
    except:
        return ''


def _get_name(block):
    try:
        return block.xpath('.//*/text()')
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
    except:
        return 'adidas'


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9]').findall(price)))
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="gl-price-item gl-price-item--sale gl-price-item--small notranslate"]/text()')[0])
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="gl-price-item gl-price-item--small notranslate"]/text()')[0])
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="gl-price-item gl-price-item--crossed gl-price-item--small notranslate"]/text()')[0])
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('//div[@class="countries__selected"]'
                          '/span[@class="countries__item-values"]/text()')[0].strip()
    except:
        return 'RUB'


def _get_site_name(block):
    return "Adidas.ru"


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
