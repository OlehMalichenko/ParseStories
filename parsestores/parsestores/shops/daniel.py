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
		# 'women': {
		# 	'Одежда': 'https://www.ennergiia.com/catalog/zhenschiny/odezhda',
		# 	'Обувь': 'https://www.ennergiia.com/catalog/zhenschiny/obuv',
		# 	'Bags': '',
		# 	'Аксессуары': 'https://www.ennergiia.com/catalog/zhenschiny/aksessuary',
		# 	'Jewels': '',
		# 	'Underwear': '',
		# 	'Perfumes': ''
		# },
		'kids': {
			'Малыши': 'https://danielonline.ru/catalogs/malyshi/',
		}
	}


def find_cat_with_titles(tree):
	result = []

	# Category
	for tag in tree.xpath('//li[contains(@class, "is-subtoggled")]'):
		title = tag.xpath('./a[@id]/text()')
		href = tag.xpath('./a[@id]/@href')
		sub1 = tag.xpath('./ul/li')

		if not title or not href:
			continue

		if not sub1:
			tit = title[0].strip()
			result.append((href[0], tit, tit, tit))

		# Category 1
		else:
			for tag1 in sub1:
				title1 = tag1.xpath('./a[@id]/text()')
				href1 = tag1.xpath('./a[@id]/@href')
				sub2 = tag1.xpath('./ul/li')

				if not title1 or not href1:
					continue

				if not sub2:
					tit = title[0].strip()
					tit1 = title1[0].strip()
					result.append((href1[0], tit, tit1, tit1))

				# Category 2
				else:
					for tag2 in sub2:
						title2 = tag2.xpath('./a[@id]/text()')
						href2 = tag2.xpath('./a[@id]/@href')


						if not title2 or not href2:
							continue

						tit = title[0].strip()
						tit1 = title1[0].strip()
						tit2 = title2[0].strip()
						result.append((href2[0], tit, tit1, tit2))
	return result


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

	product_blocks = tree.xpath('//div[@class="do-catalog-section__item"]')
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

		# if not item['id'] or not item['brand'] or not item['price']:
		# 	continue

		results.append(item)

	return results


def _get_id(block):
	try:
		return block.xpath('.//div[@data-id]/@data-id')[0]
	except:
		return ''


def _get_name(block):
	try:
		return block.xpath('.//strong[@itemprop="name"]/em/text()')[0].strip()
	except:
		return ''


def _get_brand(block):
	try:
		l = block.xpath('.//strong[@itemprop="name"]/span/text()')

		return ''.join(l).strip()
	except:
		return ''


def _create_float_price(price):

	try:
		return float(''.join(re.compile(r'[0-9]').findall(price)))
	except:
		return 0.0


def _get_price(block):
	try:
		return _create_float_price(block.xpath('.//meta[@itemprop="price"]/@content')[0])
	except:
		return 0.0


def _get_current_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@class="product__price--new"]/text()')[0])
	except:
		return 0.0


def _get_old_price(block):
	try:
		return _create_float_price(block.xpath(f'.//s/text()'))
	except:
		return 0.0


def _get_price_iso_code(tree):
	try:
		return tree.xpath('.//meta[@itemprop="priceCurrency"]/@content')[0].strip()
	except:
		return 'RUB'


def _get_site_name(block):
	return "Danielonline.ru"


def get_pagination_urls(tree, response_url):
	result = []
	max_pag_number = _get_max_pagination_number(tree)

	if max_pag_number != 1:
		for pag in range(2, max_pag_number + 1):
			result.append(f'{response_url}?PAGEN_1={pag}')

	return result


def _get_max_pagination_number(tree):
	max_num = 1
	pag_text = tree.xpath('//nav[@class="nav-pages"]/ul/li/a/text()')
	for pag_t in pag_text:
		try:
			pag_n = int(''.join(re.compile('[0-9]').findall(pag_t)))
			if pag_n > max_num:
				max_num = pag_n
		except:
			continue
	return max_num
