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
            'Одежда': 'https://timberland.ru/catalog/men/men_odezhda/',
            'Обувь': 'https://timberland.ru/catalog/men/men_obuv/',
            'Bags': '',
            'Аксессуары': 'https://timberland.ru/catalog/men/men_aksessuary/',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': 'https://timberland.ru/catalog/women/women_odezhda/',
            'Обувь': 'https://timberland.ru/catalog/women/women_obuv/',
            'Bags': '',
            'Аксессуары': 'https://timberland.ru/catalog/women/women_aksessuary/',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Малыши': 'https://timberland.ru/catalog/children/detskaya_obuv/deti_ot_1_goda_do_5_let/',
            'Дети': 'https://timberland.ru/catalog/children/detskaya_obuv/deti_ot_5_let_do_9_let/',
            'Подростки': 'https://timberland.ru/catalog/children/detskaya_obuv/deti_ot_9_let_do_13_let/'
        }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    for tag in tree.xpath('//div[@class="section section_closed js-filter-product_category list-list"]'
                          '//div[@class="list__item  "]'
                          '/label'):
        arrfil = tag.get('for')
        title = tag.text

        if arrfil is None or title is None:
            continue

        url = f'{response_url}?{arrfil}=Y&set_filter=Y&SHOWALL_2=1'

        result.append((url, title))  # !!! value list or str !!!

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

    product_blocks = tree.xpath('//div[@class="column small-6 medium-4 js-product-item ddl_product"]')
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
        return block.xpath('./@data-product-id')[0]
    except:
        return ''


def _get_name(block):
    try:
        return block.xpath('.//meta[@itemprop="name"]/@content')[0].strip()
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
    except:
        return 'Timberland'


def _create_float_price(price):
    try:
        price = ''.join(price)
        return float(''.join(re.compile(r'[0-9]').findall(price)))
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="hover-product__right-price"]'
                                               '//div[@class="price js-product-price-block js-product-price"]/text()'))
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="hover-product__right-price"]'
                                               '//div[@class="price__item js-product-discount"]/text()'))
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@class="hover-product__right-price"]'
                                               '//div[@class="price__item js-product-price"]/text()'))
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('//div[@class="countries__selected"]'
                          '/span[@class="countries__item-values"]/text()')[0].strip()
    except:
        return 'RUB'


def _get_site_name(block):
    return "Timberland.ru"


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
