import csv
from time import sleep

import requests


def get_prev_brands():
	results = set()
	with open('files/lyst_brand_shop/lyst_brands.csv', 'r', encoding='utf-8') as fp:
		reader = csv.DictReader(fp)

		for row in reader:
			results.add(row['brand'])

	return results


def get_urls():
	file_path = 'C:\\Users\\advok\\PycharmProjects\\ParseStores\\parsestores\\parsestores\\files\\lyst.txt'
	results = dict()
	prev = get_prev_brands()

	with open(file_path, 'r', encoding='utf-8') as f:
		urls = [t.strip() for t in f.readlines() if t]
		c = 0
		for url in urls:
			c += 1
			try:
				slug = [t for t in url.split('/') if t][-1]
				if slug.replace('-', ' ').replace('_', ' ').upper() in prev:
					continue
			except:
				continue
			else:
				api_url = f'https://www.lyst.com/api/rothko/modules/option_group_filtered_scroll_area/' \
				          f'?designer_slug={slug}' \
				          f'&feed_url=/explore/' \
				          f'&gender=all' \
				          f'&option_group_id=option-group-retailer-slug'
				results[slug] = api_url
			# break

	return results


def start_parse():
	urls = get_urls()

	with open('files/lyst_brand_shop/lyst_brands_p2.csv', 'a', encoding='utf-8', newline='\n') as fa:
		writer_a = csv.DictWriter(fa, fieldnames=['brand', 'retailer', 'retailer_slug', 'retailer_brand_href'])
		writer_a.writeheader()

		with open('files/lyst_brand_shop/lyst_brands_failed_p2.csv', 'a', encoding='utf-8', newline='\n') as fe:
			writer_e = csv.DictWriter(fe, fieldnames=['brand', 'url'])
			writer_e.writeheader()

			with open('files/lyst_brand_shop/lyst_brands_empty.csv', 'a', encoding='utf-8', newline='\n') as fem:
				writer_em = csv.writer(fem)

				# return
				counter = 0
				for brand_slug, url in urls.items():
					sleep(0.5)
					counter += 1
					response = requests.get(url)
					brand = brand_slug.replace('-', ' ').replace('_', ' ').upper()
					try:
						d = response.json()

						if not d['data']['options']:
							writer_em.writerow([brand, f'https://www.lyst.com/designer/{brand_slug}/'])
							print(f'-->>EMPTY<<--  https://www.lyst.com/designer/{brand_slug}/')
							continue

						for ret_block in d['data']['options']:
							tmp = dict()
							try:
								tmp['brand'] = brand
								tmp['retailer'] = ret_block['label']
								tmp['retailer_slug'] = ret_block['value']
								tmp['retailer_brand_href'] = f"https://www.lyst.com{ret_block['url']}"
								writer_a.writerow(tmp)
							except:
								continue
						print(brand)

					except Exception as e:
						writer_e.writerow({
								'brand': brand,
								'url'  : url
						})
						print(f'-----------FAILED {brand}----------')
						# print(e)
						# print(response.text)
						# pprint('\n')
						continue

				# if counter > 10:
				# 	break


if __name__ == '__main__':
	start_parse()
# get_urls()
