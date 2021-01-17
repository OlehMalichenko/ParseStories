import math
import re
from pprint import pprint

# !!!!!!!!!!!!!!!!!!!!!!!!!!!! Проблемы с определением пагинации  !!!!!!!!!!!!!!!!!!!!!!!!

def get_item_fieldnames():
    return ['id', 'name', 'category',
            'category_1', 'category_2', 'price',
            'old_price', 'price_iso_code', 'brand',
            'gender', 'site_name']


def get_urls_gender_categories():
    return {
        'men': {
            'Одежда': 'https://www.nike.com/ru/w/mens-apparel-6ymx6znik1',
            'Обувь': 'https://www.nike.com/ru/w/mens-shoes-nik1zy7ok',
            'Bags': '',
            'Аксессуары': 'https://www.nike.com/ru/w/mens-accessories-equipment-awwpwznik1',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'women': {
            'Одежда': 'https://www.nike.com/ru/w/womens-apparel-5e1x6z6ymx6',
            'Обувь': 'https://www.nike.com/ru/w/womens-shoes-5e1x6zy7ok',
            'Bags': '',
            'Аксессуары': 'https://www.nike.com/ru/w/womens-accessories-equipment-5e1x6zawwpw',
            'Jewels': '',
            'Underwear': '',
            'Perfumes': ''
        },
        'kids': {
            'Обувь': 'https://www.nike.com/ru/w/kids-shoes-v4dhzy7ok',
            'Одежда для мальчиков': 'https://www.nike.com/ru/w/boys-apparel-1onraz6ymx6',
            'Одежда для девочек': 'https://www.nike.com/ru/w/girls-apparel-3aqegz6ymx6',
            'Малыши': 'https://www.nike.com/ru/w/baby-toddler-kids-2j488zv4dh',
            'Аксессуары': 'https://www.nike.com/ru/w/kids-accessories-equipment-awwpwzv4dh'
        }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    categories = tree.xpath('//a[contains(@aria-label, "Category for")]')

    for tag in categories:
        href = tag.get('href')  # href from tag
        title = tag.text  # title from tag

        # if href is None or title is None or not href or not title:
        # 	continue

        result.append((href, title))  # !!! value list or str !!!

    return result


def find_cat2_with_title(tree, response_url):
    result = []

    categories = tree.xpath('//a[contains(@aria-label, "Category for")]')

    for tag in categories:
        href = tag.get('href')  # href from tag
        title = tag.text  # title from tag

        # if href is None or title is None or not href or not title:
        # 	continue

        result.append((href, title))  # !!! value list or str !!!

    return result


def get_items_data(tree):
    fieldnames = get_item_fieldnames()

    results = []

    product_blocks = tree.xpath('//div[contains(@class, "product-grid__card")]')
    print(len(product_blocks))

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

        # if not item['id'] or not item['brand'] or not item['price']:
        #     continue

        results.append(item)

    return results


def _get_id(block):
    try:
        return block.xpath('.//a[@class="product-card__link-overlay"]/@href')[0]
    except:
        return ''


def _get_name(block):
    try:
        return block.xpath('.//a[@class="product-card__link-overlay"]/text()')[0].strip()
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
    except:
        return 'Nike'


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9]').findall(price)))
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@data-test="product-price-reduced"]/text()')[0])
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@data-test="product-price"]/text()')[0])
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(block.xpath('.//div[@data-test="product-price"]/text()')[0])
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('//div[@class="countries__selected"]'
                          '/span[@class="countries__item-values"]/text()')[0].strip()
    except:
        return 'RUB'


def _get_site_name(block):
    return "Nike.com"


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
