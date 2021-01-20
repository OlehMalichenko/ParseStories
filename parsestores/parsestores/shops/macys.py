import math
import re
from pprint import pprint
from urllib.parse import urlsplit


def get_item_fieldnames():
    return ['id', 'name', 'category',
            'category_1', 'category_2', 'price',
            'old_price', 'price_iso_code', 'brand',
            'gender', 'site_name']


def get_urls_gender_categories():
    return {
            # 'men'  : {
            #         'Clothing'  : 'https://www.macys.com/shop/mens-clothing?id=1',
            #         'Shoes'     : '',
            #         'Bags'      : '',
            #         'Аксессуары': '',
            #         'Jewels'    : '',
            #         'Underwear' : '',
            #         'Perfumes'  : ''
            # },
            'women': {
                    'Clothing'  : 'https://www.macys.com/shop/womens-clothing?id=118',
                    'Обувь'     : '',
                    'Bags'      : '',
                    'Аксессуары': '',
                    'Jewels'    : '',
                    'Underwear' : '',
                    'Perfumes'  : ''
            },
            'kids' : {
                    'Clothing'  : 'https://www.macys.com/shop/kids-clothes?id=5991',
                    'Мальчики'  : '',
                    'Аксессуары': ''
            }
    }


def find_cat1_with_title(tree, response_url):
    result = []

    for tag_main in tree.xpath('//li[@class="accordion-category-tree"]'
                               '/div[contains(@class, "accordion")]'):  # <<-- Category level 1

        title_main_list = tag_main.xpath('.//div[@class="accordion-header-title"]/text()')
        if not title_main_list:
            continue

        marker_cat_list = ["Clothing", "Shoes", "Accessories",
                           "Jewelry", "Beauty", "Toys", ]
        category = title_main_list[0]

        for marker in marker_cat_list:
            if marker in category:
                for tag in tag_main.xpath('.//li[@class="children"]/a'):

                    title = tag.text
                    href = tag.get('href')

                    if title is None or href is None:
                        continue

                    if 'All' in title or 'New Arrivals' in title:
                        continue

                    result.append((href, category.strip(), title.strip()))

    return result


def find_cat2_with_title(tree, response_url):
    result = []

    for tag in tree.xpath('//ul[@id="facets"]/li[@id]'):
        category_mark = tag.xpath('./h2[@class="facet_name"]/@title')

        if not category_mark:
            continue

        cl = ['Category', 'Fit', 'Style', 'Type']
        mark = False
        for c in cl:
            if c in category_mark[0]:
                mark = True
        if not mark:
            continue

        for taga in tag.xpath('.//a[@class="facet_link"]'):

            href = taga.get('href')  # <<--href from tag
            title = taga.get('data-value')  # <<--title from tag

            if href is None or title is None or not href or not title:
                continue

            result.append((href, title))  # <<--value list or str

    return result


def has_deep_categories(tree):
    for tag_main in tree.xpath('//li[@class="accordion-category-tree"]'
                               '/div[contains(@class, "accordion")]'):  # <<-- Category level 1

        title_main_list = tag_main.xpath('.//div[@class="accordion-header-title"]/text()')
        if not title_main_list:
            continue

        marker_cat_list = ["Clothing", "Shoes", "Accessories",
                           "Jewelry", "Beauty", "Toys", ]
        category = title_main_list[0]

        for marker in marker_cat_list:
            if marker in category:
                return True

    return False


def get_items_data(tree):
    fieldnames = get_item_fieldnames()

    results = []

    product_blocks = tree.xpath('//div[@class="productThumbnail redesignEnabled "]')  # <-- PRODUCT BLOCKS
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
    prod_id = block.get('id')
    return prod_id if prod_id is not None else ''


def _get_name(block):
    try:
        return block.xpath('.//a[@class="productDescLink"]/@title')[0].strip()  # <<-- xpath to NAME
    except:
        return ''


def _get_brand(block):
    try:
        return block.xpath('.//div[@class="productBrand"]/text()')[0].strip()  # <<-- xpath to BRAND
    except:
        return ''


def _create_float_price(price):
    try:
        return float(''.join(re.compile(r'[0-9\\.]').findall(price)))  # <<-- CHECK REG for symbols
    except:
        return 0.0


def _get_price(block):
    try:
        return _create_float_price(
            price=''.join(block.xpath('.//span[@class="discount"]/text()')))  # <<-- xpath to PRICE
    except:
        return 0.0


def _get_current_price(block):
    try:
        return _create_float_price(
            price=''.join(block.xpath('.//span[@class="regular"]/text()')))  # <<-- xpath to ALTERNATIVE PRICE
    except:
        return 0.0


def _get_old_price(block):
    try:
        return _create_float_price(price=''.join(
            block.xpath('.//span[@class="regular originalOrRegularPriceOnSale"]/text()')))  # <<-- xpath to OLD PRICE
    except:
        return 0.0


def _get_price_iso_code(tree):
    try:
        return tree.xpath('')[0].strip()  # <<-- xpath to ISO CODE
    except:
        return 'USD'


def _get_site_name(block):
    return "Macys.com"


def get_pagination_urls(tree, response_url):
    result = []
    max_pag_number = _get_max_pagination_number(tree)

    if max_pag_number != 1:
        for pag in range(2, max_pag_number + 1):
            url = preparation_url(response_url, pag)
            result.append(url)

    return result


def _get_max_pagination_number(tree):
    max_num = 1
    pag_text = tree.xpath('//select[@id="select-page"]'
                          '/option/@value')  # <<-- xpath to PAGINATION TEXT
    for pag_t in pag_text:
        try:
            pag_n = int(''.join(re.compile('[0-9]').findall(pag_t)))
            if pag_n > max_num:
                max_num = pag_n
        except:
            continue
    return max_num


def get_filter_args_from_url(path):
    path_split = [t for t in path.split('/') if t]

    if len(path_split) > 4:
        args = path_split[-2:]
        return args[0], args[1], path_split[:-2]

    return '', '', path_split

def get_new_args(karg, varg, pag=None):
    if not karg:
        return 'Productsperpage', '120'

    karg_s = [k.strip() for k in karg.split(',') if k]
    varg_s = [v.strip() for v in varg.split(',') if v]

    arg_d = dict(zip(karg_s, varg_s))
    arg_d['Productsperpage'] = '120'
    if pag is not None:
        arg_d['Pageindex'] = f'{pag}'

    keys = ','.join(arg_d.keys())
    values = ','.join(arg_d.values())

    return keys, values


def preparation_url(url, pag=None):
    us = urlsplit(url)

    karg, varg, path_new = get_filter_args_from_url(us.path)

    keys, values = get_new_args(karg, varg, pag)

    path_new.append(keys)
    path_new.append(values)

    path = '/'.join(path_new)

    return f'{us.scheme}://{us.netloc}/{path}?{us.query}'
