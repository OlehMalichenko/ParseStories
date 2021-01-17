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
            'Обувь': 'https://jogdog.ru/catalog/men/',
            'Bags': '',
            'Аксессуары': '',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': '',
            'Обувь': 'https://jogdog.ru/catalog/women/',
            'Bags': '',
            'Аксессуары': '',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Обувь для мальчиков': 'https://jogdog.ru/catalog/child/boy/',
            'Обувь для девочек': 'https://jogdog.ru/catalog/child/girl/',
            'Обувь для малышей': 'https://jogdog.ru/catalog/child/kid/'
        }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    block_types = tree.xpath('//label[@class="elem-select js-elem-select"]')

    for tag in block_types:
        title_list = tag.xpath('./span[@class="section-title"]/text()')
        try:
            if title_list[0].strip().lower() == 'тип':
                sub_blocks = tag.xpath('./div[@class="elem-select__dropdown"]'
                                      '//a[@class="js-filter-tab-link"]')

                for atag in sub_blocks:

                    href = atag.get('href')  # href from tag
                    title = atag.get('title')  # title from tag

                    if href is None or title is None or not href or not title:
                        continue

                    result.append((href, title))  # !!! value list or str !!!

                break
        except:
            continue

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

    product_blocks = tree.xpath('//div[@class="box-catalog__item"]')
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
    return block.get('id') if block.get('id') is not None else ''


def _get_name(block):
    try:
        return block.xpath('.//span[@class="box-catalog__title"]/text()')[0].strip()
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
    except:
        return 'Jog Dog'


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9]').findall(price)))
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(block.xpath('.//span[@class="elem-price elem-price--from"]/text()')[0])
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(block.xpath('.//span[@class="product__price--new"]/text()')[0])
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(block.xpath('.//span[@class="elem-price elem-price--old"]/text()')[0])
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('//div[@class="countries__selected"]'
                          '/span[@class="countries__item-values"]/text()')[0].strip()
    except:
        return 'RUB'


def _get_site_name(block):
    return "Jogdog.ru"


def get_pagination_urls(tree, response_url):
    result = []
    max_pag_number = _get_max_pagination_number(tree)

    if max_pag_number != 1:
        for pag in range(2, max_pag_number + 1):
            result.append(f'{response_url}?PAGEN_1={pag}')

    return result


def _get_max_pagination_number(tree):
    max_num = 1
    pag_text = tree.xpath('//a[@class="box-pagination__link "]/@data-page')
    for pag_t in pag_text:
        try:
            pag_n = int(''.join(re.compile('[0-9]').findall(pag_t)))
            if pag_n > max_num:
                max_num = pag_n
        except:
            continue
    return max_num
