import math
import re
from collections import Counter
from urllib.parse import urlsplit

import demjson
import scrapy
from lxml import html
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..api_zenscrape import _api_zenscrape, _get_url_from_api
from ..items import ParseGlamItem


class LstSpider(scrapy.Spider):
    name = 'lst'
    allowed_domains = ['lyst.com']

    # TEST for debug====
    test = False
    # ==================

    # PROXY ================================
    proxy_marker = True

    #              FALSE - without zenscrape
    #              TRUE - with proxy
    # ======================================

    def start_requests(self):
        file_path = 'C:\\Users\\advok\\PycharmProjects\\ParseStores\\parsestores\\parsestores\\files\\lyst.txt'
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [t.strip() for t in f.readlines() if t]
            for url in urls:
                mask = 'https://www.lyst.com/api/rothko/modules/option_group_filtered_scroll_area/' \
                       '?designer_slug=zsigmond-dora-menswear' \
                       '&feed_url=/explore/' \
                       '&gender=all' \
                       '&option_group_id=option-group-retailer-slug'
                yield scrapy.Request(url=_api_zenscrape(url=mask,
                                                        with_proxy=self.proxy_marker),
                                     callback=self.parse,
                                     # dont_filter=True,
                                     # errback=self.errback_httpbin,
                                     # cookies=self.cookies
                                     )
                break

    def brand_alphabet_dispatch(self, response, **kwargs):
        response_url = _get_url_from_api(response_url=response.url,
                                         with_proxy=self.proxy_marker)
        print(response_url)
        print(response.url)

        # HTML===============================
        # with open('lyst.html', 'w', encoding='utf-8') as f:
        #     f.write(response.text)
        # ===================================
        # return

        tree = html.fromstring(response.text)

        # Base url
        url_s = urlsplit(response_url)
        base_url = f'{url_s.scheme}://{url_s.netloc}'

        for az_block in tree.xpath('//div[@class="brands-layout__az-block"]'):

            # TEST for debug====
            # if 'A' not in az_block.get('id'):
            # 	continue
            # ==================

            for a_tag in az_block.xpath('.//span[@class="az-block__item"]/a'):
                href = a_tag.get('href')
                title = a_tag.text

                # TEST for debug====
                # if '' not in href:
                #     continue
                # ==================

                url = f'{base_url}{href}'

                yield scrapy.Request(url=_api_zenscrape(url=url,
                                                        with_proxy=self.proxy_marker),
                                     callback=self.parse,
                                     dont_filter=True,
                                     cb_kwargs={
                                             'brand'     : title,
                                             'first_page': True
                                     },
                                     errback=self.errback_httpbin
                                     # cookies=self.cookies
                                     )
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
        with open('lyst.txt', 'w', encoding='utf-8') as f:
            f.write(response.text)
            return
        # ===================================
        tree = html.fromstring(response.text)

        brand = response.cb_kwargs['brand']
        # cl: list = response.cb_kwargs['cl']

        shops_list = tree.xpath('//div[@class="product-card__affiliate product-card__affiliate__retailer"]'
                                '/span/text()')
        shops_list = [s.strip().replace('\n', '').upper() for s in shops_list]

        c = Counter(shops_list)

        for shop, count in c.items():
            item = ParseGlamItem()
            item['brand'] = brand
            item['shop'] = shop
            item['count'] = count
            yield item

        if response.cb_kwargs['first_page']:
            max_pages = get_page_numbers(tree)
            for pag in range(2, max_pages + 1):
                try:
                    url = f'{response_url}?page={pag}'
                    yield scrapy.Request(url=_api_zenscrape(url=url,
                                                            with_proxy=self.proxy_marker),
                                         callback=self.parse,
                                         dont_filter=True,
                                         cb_kwargs={
                                                 'brand'     : brand,
                                                 'first_page': False
                                         },
                                         errback=self.errback_httpbin
                                         )
                except:
                    continue

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)


def get_page_numbers(tree):
    try:
        script = tree.xpath('//script[@data-hypernova-key="FeedsShowMore"]/text()')[0]
        start_ind = script.find('{')
        end_ind = script.rfind('}') + 1
        script = script[start_ind:end_ind]
        dscript = demjson.decode(script)
        total_prod = int(''.join(re.compile('[0-9]').findall(str(dscript['initialTotalProductCount']))))
        max_pages = math.ceil(total_prod / 48)
        return max_pages
    except:
        print('no script')
        return 0


def get_next_href(tree):
    try:
        script = tree.xpath('//script[@data-hypernova-key="FeedsShowMore"]/text()')[0]
        start_ind = script.find('{')
        end_ind = script.rfind('}') + 1
        script = script[start_ind:end_ind]
        dscript = demjson.decode(script)
        next_href = dscript['initialNextButtonUrl']
        print(f'Next href: {next_href}')
        if next_href is None or 'null' in next_href:
            return ''
        else:
            return next_href
    except:
        print('no script')
        return ''
