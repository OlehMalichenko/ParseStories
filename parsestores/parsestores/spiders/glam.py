from collections import Counter
from urllib.parse import urlsplit

import scrapy
from lxml import html

from ..api_zenscrape import _api_zenscrape, _get_url_from_api
from ..items import ParseGlamItem


class GlamSpider(scrapy.Spider):
	name = 'glam'
	allowed_domains = ['glami.ru']

	# TEST for debug====
	test = False
	# ==================

	# PROXY ================================
	proxy_marker = True

	#              FALSE - without zenscrape
	#              TRUE - with proxy
	# ======================================

	def start_requests(self):
		yield scrapy.Request(url=_api_zenscrape(url='https://www.glami.ru/brendy/',
		                                        with_proxy=self.proxy_marker),
		                     callback=self.brand_alphabet_dispatch,
		                     dont_filter=True)

	def brand_alphabet_dispatch(self, response, **kwargs):
		response_url = _get_url_from_api(response_url=response.url,
		                                 with_proxy=self.proxy_marker)

		tree = html.fromstring(response.text)

		# Base url
		url_s = urlsplit(response_url)
		base_url = f'{url_s.scheme}://{url_s.netloc}'

		for href in tree.xpath('//a[@class="alphabet__letter"]/@href'):

			# TEST for debug====
			if '/brendy/A/' in href:
				continue
			# ==================

			url = f'{base_url}{href}'
			yield scrapy.Request(url=_api_zenscrape(url=url,
			                                        with_proxy=self.proxy_marker),
			                     callback=self.brand_dispatch,
			                     dont_filter=True)
			if self.test:
				break

	def brand_dispatch(self, response, **kwargs):
		response_url = _get_url_from_api(response_url=response.url,
		                                 with_proxy=self.proxy_marker)
		tree = html.fromstring(response.text)

		# Base url
		url_s = urlsplit(response_url)
		base_url = f'{url_s.scheme}://{url_s.netloc}'

		for a_tag in tree.xpath('//a[@class="brand"]'):
			href = a_tag.get('href')
			title = a_tag.xpath('./span[@class="title"]/text()')
			if href is None or not title:
				continue

			# TEST for debug====
			# if '/chloe/' not in href:
			#     continue
			# ==================

			yield scrapy.Request(url=_api_zenscrape(url=f'{base_url}{href}',
			                                        with_proxy=self.proxy_marker),
			                     callback=self.parse,
			                     dont_filter=True,
			                     cb_kwargs={
					                     'brand': title[0].strip(),
					                     'cl'   : []
			                     })
			if self.test:
				break

	def parse(self, response, **kwargs):
		response_url = _get_url_from_api(response_url=response.url,
		                                 with_proxy=self.proxy_marker)
		print(response_url)

		# Base url
		url_s = urlsplit(response_url)
		base_url = f'{url_s.scheme}://{url_s.netloc}'

		# HTML===============================
		# with open('glam.html', 'w', encoding='utf-8') as f:
		#     f.write(response.text)
		# ===================================
		tree = html.fromstring(response.text)

		brand = response.cb_kwargs['brand']
		cl: list = response.cb_kwargs['cl']

		shops_list = tree.xpath('//span[@class="item__provider-name"]/@title')
		cl = cl + shops_list

		next = tree.xpath('//a[@rel="next"]/@href')
		if next:
			yield scrapy.Request(url=_api_zenscrape(url=f'{base_url}{next[0]}',
			                                        with_proxy=self.proxy_marker),
			                     callback=self.parse,
			                     dont_filter=True,
			                     cb_kwargs={
					                     'brand': brand,
					                     'cl'   : cl
			                     })
		else:
			c = Counter(cl)
			for shop, count in c.items():
				item = ParseGlamItem()
				item['brand'] = brand
				item['shop'] = shop
				item['count'] = count
				yield item

		# reg = re.compile('[0-9]')
		#
		# for li in tree.xpath('//ul[@class="attribute-values provider attribute-all-provider"]/li'):
		#     c = li.get('data-count')
		#     s = li.xpath('.//span[@class="title"]/text()')
		#     print(f'Count: {c}')
		#     print(f'Shop: {s}')
		#     if c is None or not s:
		#         continue
		#
		#     try:
		#         count = int(''.join(reg.findall(c)))
		#         shop = s[0].strip()
		#     except:
		#         continue
		#
		#     item = ParseGlamItem()
		#     item['brand'] = brand
		#     item['shop'] = shop
		#     item['count'] = count
		#
		#     yield item
