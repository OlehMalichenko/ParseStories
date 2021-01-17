from urllib.parse import urlsplit
import scrapy
from lxml import html
from ..items import ParsestoresItem
from ..api_zenscrape import _api_zenscrape, _get_url_from_api

# CHECK SHOP =====================
from ..shops.jogdog import *
# ================================


class AaaSpider(scrapy.Spider):
    name = 'aaa'
    allowed_domains = []

    # TEST for debug====
    test = False
    # ==================

    # PROXY ================================
    proxy_marker = False
    #              FALSE - without zenscrape
    #              TRUE - with proxy
    # ======================================

    def start_requests(self):
        urls_d = get_urls_gender_categories()

        for gender, cat_d in urls_d.items():
            for cat, url in cat_d.items():
                if not url:
                    continue
                # print(f'start: {url}')
                yield scrapy.Request(url=_api_zenscrape(url=url,
                                                        with_proxy=self.proxy_marker),
                                     callback=self.cat1_disp,
                                     dont_filter=True,
                                     meta={
                                         'gender': gender,
                                         'category': cat,
                                         'category_1': cat,
                                         'category_2': cat,
                                         'first_page': True

                                     })
            # TEST ===========
                if self.test:
                    break
            if self.test:
                break
            # ===============

    def cat_disp(self, response):
        response_url = _get_url_from_api(response_url=response.url,
                                         with_proxy=self.proxy_marker)
        # print(response_url)

        # Base url
        url_s = urlsplit(response_url)
        base_url = f'{url_s.scheme}://{url_s.netloc}'

        # Meta data
        gender = response.meta['gender']
        category = response.meta['category']

        tree = html.fromstring(response.text)

        c = 0
        for ht in find_cat1_with_title(tree, response_url):
            c += 1
            # pprint(ht)

            # Create deep url
            deep_url = f'{base_url}{ht[0]}'  # ! for href !
            # deep_url = ht[0]  # ! for url !

            yield scrapy.Request(url=_api_zenscrape(url=deep_url,
                                                    with_proxy=self.proxy_marker),
                                 callback=self.parse,
                                 dont_filter=True,
                                 meta={
                                     'gender': gender,
                                     'category': ht[1],
                                     'category_1': ht[2],
                                     'category_2': ht[3],
                                     'first_page': True
                                 })
            # TEST ===========
            if self.test and c > 1:
                break
            # ================

    def cat1_disp(self, response):
        response_url = _get_url_from_api(response_url=response.url,
                                         with_proxy=self.proxy_marker)
        # print(response_url)

        # Base url
        url_s = urlsplit(response_url)
        base_url = f'{url_s.scheme}://{url_s.netloc}'

        # Meta data
        gender = response.meta['gender']
        category = response.meta['category']

        tree = html.fromstring(response.text)

        not_category_1 = True

        for ht in find_cat1_with_title(tree, response_url):
            # pprint(ht)

            # Create deep url
            deep_url = f'{base_url}{ht[0]}'  # ! for href !
            # deep_url = ht[0]  # ! for url !

            yield scrapy.Request(url=_api_zenscrape(url=deep_url,
                                                    with_proxy=self.proxy_marker),
                                 callback=self.parse,
                                 dont_filter=True,
                                 meta={
                                     'gender': gender,
                                     'category': category,
                                     'category_1': ht[1],
                                     'category_2': ht[1],
                                     'first_page': True
                                 })
            not_category_1 = False
            # TEST ===========
            if self.test:
                break
            # ================

        # if not_category_1:
        #     yield scrapy.Request(url=_api_zenscrape(url=response_url,
        #                                             with_proxy=self.proxy_marker),
        #                          callback=self.parse,
        #                          dont_filter=True,
        #                          meta={
        #                              'gender': gender,
        #                              'category': category,
        #                              'category_1': category,
        #                              'category_2': category,
        #                              'first_page': True
        #                          })

    def cat2_disp(self, response):
        # print(response.url)
        response_url = _get_url_from_api(response_url=response.url,
                                         with_proxy=self.proxy_marker)

        # Base url
        url_s = urlsplit(response_url)
        base_url = f'{url_s.scheme}://{url_s.netloc}'

        # Meta data
        gender = response.meta['gender']
        category = response.meta['category']
        category_1 = response.meta['category_1']

        tree = html.fromstring(response.text)

        not_category_2 = True

        for ht in find_cat2_with_title(tree, response_url):
            # pprint(ht)
            # Create deep url
            # deep_url = f'{base_url}{ht[0]}'  # ! for href !
            deep_url = ht[0]  # ! for url !
            # print(deep_url, ht[1])

            yield scrapy.Request(url=_api_zenscrape(url=deep_url,
                                                    with_proxy=self.proxy_marker),
                                 callback=self.parse,
                                 dont_filter=True,
                                 meta={
                                     'gender': gender,
                                     'category': category,
                                     'category_1': category_1,
                                     'category_2': ht[1].strip(),
                                     'first_page': True
                                 })
            not_category_2 = False

            # TEST ===========
            if self.test:
                break
            # ================

        if not_category_2:
            yield scrapy.Request(url=_api_zenscrape(url=response_url,
                                                    with_proxy=self.proxy_marker),
                                 callback=self.parse,
                                 dont_filter=True,
                                 meta={
                                     'gender': gender,
                                     'category': category,
                                     'category_1': category_1,
                                     'category_2': category_1,
                                     'first_page': True
                                 })

    def parse(self, response, **kwargs):
        response_url = _get_url_from_api(response_url=response.url,
                                         with_proxy=self.proxy_marker)
        print(response_url)

        # HTML===============================
        # with open('adidas.html', 'w') as f:
        #     f.write(response.text)
        # ===================================

        gender = response.meta['gender']
        category = response.meta['category']
        category_1 = response.meta['category_1']
        category_2 = response.meta['category_2']
        first_page = response.meta['first_page']
        # print(gender, category, category_1, category_2, first_page)

        tree = html.fromstring(response.text)

        # Products
        items_data = get_items_data(tree)
        # pprint(items_data)

        for item_data in items_data:
            item = ParsestoresItem()

            for k, v in item_data.items():
                item[k] = v

            item['gender'] = gender
            item['category'] = category
            item['category_1'] = category_1
            item['category_2'] = category_2
            # pprint(item)

            yield item
        #
        # # ==========Pagination NEXT
        #
        # next_pagination_url = get_pagination_urls(tree, response_url)
        # if next_pagination_url:
        #     yield scrapy.Request(url=_api_zenscrape(url=next_pagination_url,
        #                                             with_proxy=self.proxy_marker),
        #                          callback=self.parse,
        #                          dont_filter=True,
        #                          meta={
        #                              'gender': gender,
        #                              'category': category,
        #                              'category_1': category_1,
        #                              'category_2': category_2,
        #                              'first_page': False
        #                          })

        # Pagination ALL URLS
        if first_page:
            next_pagination_urls = get_pagination_urls(tree, response_url)
            # pprint(next_pagination_urls)
            for url_next in next_pagination_urls:
                yield scrapy.Request(url=_api_zenscrape(url=url_next,
                                                        with_proxy=self.proxy_marker),
                                     callback=self.parse,
                                     dont_filter=True,
                                     meta={
                                         'gender': gender,
                                         'category': category,
                                         'category_1': category_1,
                                         'category_2': category_2,
                                         'first_page': False
                                     })
                # TEST ===========
                if self.test:
                    break
                # ================
