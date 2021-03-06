import math
import re
from pprint import pprint

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Необходим рендеринг !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

def get_item_fieldnames():
	return ['id', 'name', 'category',
	        'category_1', 'category_2', 'price',
	        'old_price', 'price_iso_code', 'brand',
	        'gender', 'site_name']


def get_urls_gender_categories():
	return {
			'men'  : {
					'Одежда'    : 'https://www.guess.ru/ru/',
					'Обувь'     : '',
					'Bags'      : '',
					'Аксессуары': '',
					'Jewels'    : '',
					'Underwear' : '',
					'Perfumes'  : ''
			},
			'women': {
					'Одежда'    : '',
					'Обувь'     : '',
					'Bags'      : '',
					'Аксессуары': '',
					'Jewels'    : '',
					'Underwear' : '',
					'Perfumes'  : ''
			},
			'kids' : {
					'Девочки'   : '',
					'Мальчики'  : '',
					'Аксессуары': ''
			}
	}


def find_cat1_with_title(tree, response_url):
	result = []

	sub = tree.xpath('//li[contains(@class, "menuItem depth1")]')
	print(f'sub: {len(sub)}')

	for depth1 in sub:
		t_list = depth1.xpath('./div[@class="menuItemTitleContainer"]'
		                      '/a[@class="menuItemTitleLink"]/text()')
		if not t_list:
			continue

		gender = ''
		if 'ЖЕНЩИН' in t_list[0]:
			gender = 'women'
		elif 'МУЖЧИН' in t_list[0]:
			gender = 'men'
		elif 'СУМК' in t_list[0]:
			gender = 'women'
		else:
			continue

		print(f'gender: {gender}')

		for depth2 in depth1.xpath('./div[@class="menuItemChildrenContainer"]//li[contains(@class, "menuItem depth2")]'):
			try:
				title = depth2.xpath('./div[@class="menuItemTitleContainer"]/a[@class="menuItemTitleLink"]/text()')
				href = depth2.xpath('./div[@class="menuItemTitleContainer"]/a[@class="menuItemTitleLink"]/@href')
				sub1 = depth2.xpath('./div[@class="menuItemChildrenContainer"]//li[contains(@class, "menuItem depth3")]')
			except:
				continue

			if not sub1:
				result.append((href, title, title, title, gender))

			else:
				print(f'sub1: {len(sub1)}')
				for depth3 in sub1:
					try:
						title1 = depth3.xpath('./div[@class="menuItemTitleContainer"]/a[@class="menuItemTitleLink"]/text()')[0].strip()
						href1 = depth3.xpath('./div[@class="menuItemTitleContainer"]/a[@class="menuItemTitleLink"]/@href')[0]
						sub2 = depth3.xpath('./div[@class="menuItemChildrenContainer"]//li[contains(@class, "menuItem depth4")]')
					except:
						continue

					if not sub2:
						result.append((href1, title, title1, title1, gender))

					else:
						print(f'sub2: {len(sub2)}')
						for depth4 in sub2:
							try:
								title2 = depth4.xpath('./div[@class="menuItemTitleContainer"]/a[@class="menuItemTitleLink"]/text()')[0].strip()
								href2 = depth4.xpath('./div[@class="menuItemTitleContainer"]/a[@class="menuItemTitleLink"]/@href')[0]
							except:
								continue

							result.append((href2, title, title1, title2, gender))

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

	product_blocks = tree.xpath('//div[@class="col-xs-6 col-md-6 col-lg-4 product-list-wrapper"]')
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
		return block.xpath('./div[@class="product-preview"]'
		                   '/a/@href')[0]
	except:
		return ''


def _get_name(block):
	try:
		return block.xpath('.//div[contains(@class, "product-preview__name")]/text()')[0].strip()
	except:
		return ''


def _get_brand(block):
	try:
		return block.xpath('.//div[contains(@class, "product-preview__brand")]/text()')[0].strip()
	except:
		return ''


def _create_float_price(price):
	try:
		return float(''.join(re.compile(r'[0-9]').findall(price)))
	except:
		return 0.0


def _get_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@data-test="product-price-active"]/text()')[0])
	except:
		return 0.0


def _get_current_price(block):
	try:
		return _create_float_price(block.xpath('.//span[@class="product__price--new"]/text()')[0])
	except:
		return 0.0


def _get_old_price(block):
	try:
		return _create_float_price(block.xpath('.//div[contains(@class, "price_old")]/@aria-label')[0])
	except:
		return 0.0


def _get_price_iso_code(tree):
	try:
		return tree.xpath('//div[@class="countries__selected"]'
		                  '/span[@class="countries__item-values"]/text()')[0].strip()
	except:
		return 'RUB'


def _get_site_name(block):
	return "Ennergiia.com"


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
