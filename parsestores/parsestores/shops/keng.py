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
		# 	'Одежда': '',
		# 	'Обувь': '',
		# 	'Bags': '',
		# 	'Аксессуары': '',
		# 	'Jewels': '',
		# 	'Underwear': '',
		# 	'Perfumes': ''
		# },
		'women': {
			'Одежда': 'https://www.keng.ru/catalog/zhenskie-kollekcii-odezhda/',
			# 'Обувь': 'https://www.keng.ru/catalog/zhenskie-kollekcii-obuv/',
			# 'Верхняя одежда': 'https://www.keng.ru/catalog/zhenskie-kollekcii-verkhnyaya-odezhda/',
			# 'Аксессуары': 'https://www.keng.ru/catalog/zhenskie-kollekcii-aksessuary/',
			# 'Нарядная одежда': 'https://www.keng.ru/catalog/zhenskie-kollektsii-naryadnaya-odezhda/',
			# 'Белье': 'https://www.keng.ru/catalog/zhenskie-kollekcii-bele/',
			# 'Perfumes': ''
		},
		'kids': {
			'Девочки': 'https://www.ennergiia.com/catalog/deti/devochki',
			'Мальчики': 'https://www.ennergiia.com/catalog/deti/malchiki',
			'Аксессуары': 'https://www.ennergiia.com/catalog/deti/aksessuary',
			'Малыши': 'https://www.keng.ru/catalog/malyshi/',
			'Детская обувь': 'https://www.keng.ru/catalog/detskaya-obuv/',
		}
	}


def find_cat1_with_title(tree, response_url):
	result = []

	for tag in tree.xpath('//div[@class="list__item item--category"]'):
		href = tag.xpath('.//a[contains(@class, "list__item--link")]/@href')  # href from tag
		title = tag.xpath('.//span[@class="list__item--span"]/text()')  # title from tag

		if not href or not title:
			continue

		tags1 = tag.xpath('.//ul[@class="list__item--drop"]/li/a')
		if tags1:
			for tag1 in tags1:
				href1 = tag1.get('href')
				title1 = tag1.text

				if href1 is None or title1 is None:
					continue

				result.append((href1, title[0].strip(), title1, title1))
		else:
			result.append((href[0], title[0].strip(), title[0].strip(), title[0].strip()))

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

	product_blocks = tree.xpath('//li[@class="cards__string--block "]')
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
		return block.xpath('.//a[@class="gtag-item-click block__category--link"]/@data-id')[0]
	except:
		return ''


def _get_name(block):
	try:
		return block.xpath('.//a[@class="gtag-item-click block__category--link"]/text()')[0].strip()
	except:
		return ''


def _get_brand(block):
	try:
		return block.xpath('.//a[@class="gtag-item-click block__title--link"]/text()')[0].strip()
	except:
		return ''


def _create_float_price(price):
	try:
		return float(''.join(re.compile(r'[0-9]').findall(price)))
	except:
		return 0.0


def _get_price(block):
	try:
		return _create_float_price(block.xpath('.//div[@class="block__price"]/text()')[0])
	except:
		return 0.0


def _get_current_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@class="product__price--new"]/text()')[0])
	except:
		return 0.0


def _get_old_price(block):
	try:
		return _create_float_price(block.xpath('.//div[@class="block__price"]/s/text()')[0])
	except:
		return 0.0


def _get_price_iso_code(tree):
	try:
		return tree.xpath('//div[@class="countries__selected"]'
		                  '/span[@class="countries__item-values"]/text()')[0].strip()
	except:
		return 'RUB'


def _get_site_name(block):
	return "Keng.ru"


def get_pagination_urls(tree, response_url):
	result = []
	max_pag_number = _get_max_pagination_number(tree)

	if max_pag_number != 1:
		for pag in range(2, max_pag_number + 1):
			result.append(f'{response_url}?page={pag}')

	return result


def _get_max_pagination_number(tree):
	max_num = 1
	pag_text = tree.xpath('//a[@class="paging__item--link "]/text()')
	for pag_t in pag_text:
		try:
			pag_n = int(''.join(re.compile('[0-9]').findall(pag_t)))
			if pag_n > max_num:
				max_num = pag_n
		except:
			continue
	return max_num
