import requests
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from products.models import Product  

class TexnoSmartParser:
    def __init__(self):
        self.base_url = 'https://texnosmart.by'
        self.categories = [
            'https://texnosmart.by/mobile',

        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_soup(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            print(f"[Network Error] {url}: {e}")
        return None

    def clean_text(self, elem):
        return elem.get_text(strip=True) if elem else ''

    def clean_price(self, price_str):
        if not price_str:
            return 0.0
        clean = price_str.replace('руб.', '').replace(' ', '').replace(',', '.')
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def get_product_links(self, category_url):
        links = []
        soup = self.get_soup(category_url)
        if not soup:
            return []

        pagination = soup.find('ul', class_='pagination no-margin-top')
        if pagination:
            pages = [int(li.text) for li in pagination.find_all('li') if li.text.isdigit()]
            last_page = max(pages) if pages else 1
        else:
            last_page = 1
        last_page = 2
        print(f"Категория {category_url}: найдено страниц {last_page}")

        for page in range(1, last_page + 1):
            page_url = f"{category_url}?page={page}"
            s = self.get_soup(page_url)
            if not s: 
                continue

            product_cards = s.find(id='productsList')
            if product_cards:
                items = product_cards.find_all(class_='item')
                for product in items:
                    try:
                        desc_block = product.find(class_='description')
                        link_tag = desc_block.find(class_='info-level4').find('a')
                        href = link_tag.get('href')
                        links.append(f"{self.base_url}/{href.lstrip('/')}")
                    except AttributeError:
                        continue
        return links

    def parse_detail(self, url):
        soup = self.get_soup(url)
        if not soup:
            return None

        try:
            title = self.clean_text(soup.find(class_='product-title'))
            price_text = self.clean_text(soup.find(class_='product-price'))
            price = self.clean_price(price_text)
            description = self.clean_text(soup.find(class_='details-description'))
            status = self.clean_text(soup.find(class_='availability-1 incaps info-level3'))

            image_block = soup.find('div', class_='col-lg-6 col-md-6 col-sm-6')
            image_link = image_block.find('a') if image_block else None
            image_url = f"{self.base_url}/{image_link['href'].lstrip('/')}" if image_link else ''

            specs = {}
            details_div = soup.find("div", id="details")
            if details_div:
                rows = details_div.find_all("tr", class_="product-item")
                for row in rows:
                    tds = row.find_all("td")
                    if len(tds) == 2:
                        key = tds[0].get_text(strip=True)
                        value = tds[1].get_text(" ", strip=True)
                        specs[key] = value

            return {
                'title': title,
                'price': price,
                'link': url,
                'description': description,
                'image_url': image_url,
                'status': status,
                'specs': specs,
                'store': 'TexnoSmart'
            }
        except Exception as e:
            print(f"[Parse Error] {url}: {e}")
            return None

    def save_to_mongo(self, data):
        if not data:
            return

        product = Product.objects(link=data['link']).first()

        if not product:
            product = Product(link=data['link'])
            product.article = f"TS-{random.randint(100000, 999999)}"

        product.title = data['title']
        product.price = data['price']
        product.description = data['description']
        product.image_url = data['image_url']
        product.status = data['status']
        product.specs = data['specs']
        product.store = data['store']

        product.save()
        print(f"Saved: {product.title}")

    def run(self):
        all_links = []
        
        print("Сбор ссылок...")
        for cat in self.categories:
            links = self.get_product_links(cat)
            all_links.extend(links)
        
        print(f"Всего ссылок для обработки: {len(all_links)}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.parse_detail, url): url for url in all_links}
            
            for future in as_completed(future_to_url):
                data = future.result()
                if data:
                    self.save_to_mongo(data)

class Command(BaseCommand):
    help = 'Парсинг TexnoSmart'

    def handle(self, *args, **options):
        parser = TexnoSmartParser()
        parser.run()
        self.stdout.write(self.style.SUCCESS('Парсинг завершен!'))