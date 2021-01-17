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
			# 'Одежда': 'https://vans.ru/catalog/men/category/odezhda/',
			'Обувь': 'https://vans.ru/catalog/men/category/obuv/',
			'Bags': '',
			'Аксессуары': 'https://vans.ru/catalog/men/category/aksessuary/',
			'Jewels': '',
			'Underwear': '',
			'Perfumes': ''
		},
		'women': {
			'Одежда': 'https://vans.ru/catalog/women/category/odezhda/',
			'Обувь': 'https://vans.ru/catalog/women/category/obuv/',
			'Bags': '',
			'Аксессуары': 'https://vans.ru/catalog/women/category/aksessuary/',
			'Jewels': '',
			'Underwear': '',
			'Perfumes': ''
		},
		'kids': {
			'Обувь': 'https://vans.ru/catalog/kids/',
			'Мальчики': '',
			'Аксессуары': ''
		}
	}


def find_cat1_with_title(tree, response_url):
	result = []

	try:
		script = tree.xpath(f'//script[contains(text(), "window.filter =")]/text()')[0]
		start = script.find('{')
		script = script[start:].strip()
	except:
		print('script_text')
		return result

	try:
		script_d = demjson.decode(script)
	except:
		print('decode json')
		return result

	try:
		fields_blocks = []

		for c in script_d['fields']['categories']:
			try:
				if 'CATEGORY' in c['code']:
					fields_blocks = c['values']
					break
			except:
				continue
	except:
		print('find categories')
		return result


	for block in fields_blocks:
		try:
			title = block["title"]
			url = f'{response_url}filter/price-base-from-1195-to-12790/category-is-{title.lower()}/apply/?sort=new'
			result.append((url, title))
		except:
			continue




	# for tag in tree.xpath('//script[contains(text(), "window.filter =")]/text()'):
	# 	data_test = tag.get('data-test')  # href from tag
	# 	title = tag.xpath('./span/text()')  # title from tag
	#
	# 	if data_test is None or title is None or not data_test or not title:
	# 		continue
	#
	# 	result.append((f'{response_url}/{data_test}', title[0]))  # !!! value list or str !!!

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

	product_blocks = tree.xpath('//li[@class="catalog-content__item"]')
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
		#     item['price'] = _get_current_price(block)

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
		return block.xpath('.//a[@class="catalog-item__image"]/@data-impression-data-item-id')[0]
	except:
		return ''


def _get_name(block):
	try:
		return block.xpath('.//a[@class="catalog-item__image"]/@data-impression-data-name')[0]
	except:
		return ''


def _get_brand(block):
	try:
		return block.xpath('.//a[@class="catalog-item__image"]/@data-impression-data-brand')[0]
	except:
		return ''


def _create_float_price(price):
	try:
		return float(''.join(re.compile(r'[0-9]').findall(price)))
	except:
		return 0.0


def _get_price(block):
	try:
		return _create_float_price(block.xpath('.//a[@class="catalog-item__image"]/@data-impression-data-price')[0])
	except:
		return 0.0


def _get_current_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@class="product__price--new"]/text()')[0])
	except:
		return 0.0


def _get_old_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@class="catalog-item__price m-old"]/text()')[0])
	except:
		return 0.0


def _get_price_iso_code(tree):
	try:
		return tree.xpath('//div[@class="countries__selected"]'
		                  '/span[@class="countries__item-values"]/text()')[0].strip()
	except:
		return 'RUB'


def _get_site_name(block):
	return "Vans.ru"


def get_pagination_urls(tree, response_url):
	result = []
	max_pag_number = _get_max_pagination_number(tree)

	if max_pag_number != 1:
		for pag in range(2, max_pag_number + 1):
			result.append(f'{response_url}&PAGEN_1={pag}')

	return result


def _get_max_pagination_number(tree):
	max_num = 1
	try:
		pag_text = tree.xpath('//ul[@data-count-pages]/@data-count-pages')[0].strip()
		return int(pag_text)
	except:
		return max_num

