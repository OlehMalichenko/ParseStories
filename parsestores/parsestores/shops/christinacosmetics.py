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
		# 'men': {
		# 	'Одежда': 'https://www.ennergiia.com/catalog/muzhchiny/odezhda',
		# 	'Обувь': 'https://www.ennergiia.com/catalog/muzhchiny/obuv',
		# 	'Bags': '',
		# 	'Аксессуары': 'https://www.ennergiia.com/catalog/muzhchiny/aksessuary',
		# 	'Jewels': '',
		# 	'Underwear': '',
		# 	'Perfumes': ''
		# },
		'women': {
			# 'Одежда': 'https://www.ennergiia.com/catalog/zhenschiny/odezhda',
			# 'Обувь': 'https://www.ennergiia.com/catalog/zhenschiny/obuv',
			'Косметика': 'https://christinacosmetics.ru/shop/',
			# 'Аксессуары': 'https://www.ennergiia.com/catalog/zhenschiny/aksessuary',
			'Jewels': '',
			'Underwear': '',
			'Perfumes': ''
		},
		# 'kids': {
		# 	'Девочки': 'https://www.ennergiia.com/catalog/deti/devochki',
		# 	'Мальчики': 'https://www.ennergiia.com/catalog/deti/malchiki',
		# 	'Аксессуары': 'https://www.ennergiia.com/catalog/deti/aksessuary'
		# }
	}


def find_cat1_with_title(tree, response_url):
	result = []

	for tag in tree.xpath('//div[@class="categories-list categories-list__sub-menu"]'
	                      '//div[@data-test]'):
		data_test = tag.get('data-test')  # href from tag
		title = tag.xpath('./span/text()')  # title from tag

		if data_test is None or title is None or not data_test or not title:
			continue

		result.append((f'{response_url}/{data_test}', title[0]))  # !!! value list or str !!!

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

	product_blocks = tree.xpath('//div[@class="col-lg-4 col-md-6 col-sm-6"]')
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
		# if not item['price']:
		#     item['price'] = _get_current_price(block)

		# Old_price
		item['old_price'] = _get_old_price(block)

		# Price ICO Code
		item['price_iso_code'] = _get_price_iso_code(block)

		# Site name
		item['site_name'] = _get_site_name('block')

		item['category'], item['category_1'], item['category_2'] = get_categories(block)

		if not item['id'] or not item['brand'] or not item['price'] or not item['category'] or not item['category_1'] or not item['category_2']:
			continue

		results.append(item)

	return results


def _get_id(block):
	try:
		return block.xpath('.//div[@class="item-catalog"]/@id')[0]
	except:
		return ''


def _get_name(block):
	try:
		return block.xpath('.//a[@class="item-catalog__name"]/text()')[0].strip()
	except:
		return ''


def _get_brand(block):
	try:
		return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
	except:
		return 'Christina'


def _create_float_price(price):
	try:
		return float(''.join(re.compile(r'[0-9]').findall(price)))
	except:
		return 0.0


def _get_price(block):
	try:
		return _create_float_price(''.join(block.xpath('.//div[@class="item-catalog__price"]/text()')))
	except:
		return 0.0


def _get_current_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@class="product__price--new"]/text()')[0])
	except:
		return 0.0


def _get_old_price(block):
	try:
		return _create_float_price(block.xpath('.//div[@class="item-catalog__price"]/s/text()')[0])
	except:
		return 0.0


def _get_price_iso_code(tree):
	try:
		return tree.xpath('//div[@class="countries__selected"]'
		                  '/span[@class="countries__item-values"]/text()')[0].strip()
	except:
		return 'RUB'


def _get_site_name(block):
	return "Christinacosmetics.ru"


def get_pagination_urls(tree, response_url):
	result = []
	max_pag_number = _get_max_pagination_number(tree)

	if max_pag_number != 1:
		for pag in range(2, max_pag_number + 1):
			result.append(f'{response_url}?page={pag}')

	return result


def get_categories(block):
	category = ''
	category_1 = ''
	category_2 = ''

	try:
		cat_list = block.xpath('.//span[contains(@class, "list-tags__")]/text()')
		cat_list.sort()
		if len(cat_list) > 1:
			category = '/'.join(cat_list)
			category_1 = cat_list[1]
			category_2 = cat_list[2] if len(cat_list) > 2 else category_1

	except:
		return '' * 3

	return category, category_1, category_2


def get_next_pagination_url(tree):
	try:
		next_href = tree.xpath('//a[@class="pagination__arrow pagination__arrow_next"]/@href')[0]
		next_href = next_href.replace('PAGEN_10', 'PAGEN_8')
		return f'https://christinacosmetics.ru{next_href}'
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
