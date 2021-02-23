import re

import scrapy
from lxml import html

from ..api_zenscrape import _api_zenscrape, _get_url_from_api


class MrkSpider(scrapy.Spider):
	name = 'mrk'
	allowed_domains = ['marketplace.asos.com']

	# TEST for debug====
	test = True
	# ==================

	# PROXY ================================
	proxy_marker = True

	#              FALSE - without zenscrape
	#              TRUE - with proxy
	# ======================================

	def start_requests(self):
		yield self.scrapy_Request(url='https://marketplace.asos.com/boutiques',
		                          callback_method=self.boutiques_dispatch,
		                          cb_kwargs={
				                          'first_page': True
		                          })

	def boutiques_dispatch(self, response, **kwargs):
		response_url = _get_url_from_api(response.url)
		print(response_url)
		first_page = response.cb_kwargs['first_page']

		tree = html.fromstring(response.text)
		for a_tag in tree.xpath('//a[@class="notranslate"]'):
			href = a_tag.get('href')
			title = a_tag.text
			if href is None or title is None:
				continue
			url_boutique = f'https://marketplace.asos.com{href}'
			yield self.scrapy_Request(url=url_boutique,
			                          callback_method=self.parse,
			                          cb_kwargs={
					                          'btq': title
			                          })
			if self.test:
				break

		if first_page:
			max_pag_number = get_max_pag_number(tree)
			for pag in range(2, max_pag_number + 1):
				url = f'{response_url}?pgno={pag}'
				# print(f'-------------{url}')
				yield self.scrapy_Request(url=url,
				                          callback_method=self.boutiques_dispatch,
				                          cb_kwargs={
						                          'first_page': False
				                          })
				if self.test:
					break

	def parse(self, response, **kwargs):
		pass

	def scrapy_Request(self, url, callback_method, cb_kwargs=None):
		if cb_kwargs is None:
			cb_kwargs = {}
		return scrapy.Request(url=_api_zenscrape(url=url,
		                                         with_proxy=self.proxy_marker),
		                      callback=callback_method,
		                      dont_filter=True,
		                      cb_kwargs=cb_kwargs
		                      )


def get_max_pag_number(tree):
	page_numbers = tree.xpath('//div[@class="page"]'
	                          '//a/@data-page-number')
	reg = re.compile('[0-9]')
	mx = 0
	for i in page_numbers:
		try:
			num = int(''.join(reg.findall(str(i))))
			if num > mx:
				mx = num
		except:
			continue
	return mx
