from scrapy import Spider
from scrapy.http import Request
import os
import re
import requests
import time

class AmazonSpiderSpider(Spider):
    name = 'amazon_spider'
    allowed_domains = ['www.amazon.in/']
    start_urls = []
    other_urls = []
    counter = 0
    MAX_CNT = 20
    def __init__(self):
        search = input("Enter the items you wanna search separated by spaces : ").split()
        cnt = 0
        for item in search:
            link = f"https://www.amazon.in/s?k={item}"
            if cnt == 0:
                self.start_urls.append(link)
            else:
                self.other_urls.append(link)
            cnt = cnt + 1
            
    def parse(self, response):
        parent_dir = "C:/Users/805313/Documents/Jupyter Python Projects/Web Essentials using Python/Web Crawler/amazon_scrapping/Crawled_Items"
        directory = response.url[response.url.find('=') + 1:]
        # print(directory)
        path = os.path.join(parent_dir, directory)
        self.create_dir(path)
        all_links = response.xpath('//h2/a/@href').extract()[:self.MAX_CNT]
        # print(all_links)
        items = response.xpath('//h2/a/span/text()').extract()[:self.MAX_CNT]
        # print(items)
        index = 0
        for link in all_links:
            item = items[index]    
            index = index + 1 
            item_short = item[ : item.find(')') + 1]
            # print(item_short)
            if len(item_short) == 0 :
                item_short = item
            # print(item_short)
            item_short = item_short[:30]
            item_short = ''.join(e for e in item_short if (e.isalnum() or e.isspace()))
            item_short = item_short.strip()
            p = os.path.join(path, item_short)
            # print(p)
            page = response.urljoin(link)
            # print(page)
            if page is not None:
                yield Request(url = page, callback = self.parse_pages, meta = {'path' : p}, dont_filter = True)

        
        
    def parse_pages(self, response, **meta):
        features = response.xpath('//div[@id="feature-bullets"]/ul/li/span[@class="a-list-item"]/text()').extract()
        features = "".join(features)
        features = ''.join(e for e in features if (e.isalnum() or e.isspace()))
        features = bytes(features, 'utf-8')
        images = re.findall('(?<=\"hiRes":").+?(?=\",)', ','.join(response.css('script').extract()))
        images = list(set(images[:10]))
        path = response.meta['path']
        # print(path)
        self.create_dir(path)
        with open(f'{path}/meta.txt', 'wb') as file:
            file.write(features)
        # print(images)
        index = 0
        for image in images:
            # self.create_dir(path)
            filename = f'{path}/{index + 1}.jpg'
            # print(filename)
            index = index + 1
            # print(image_select)
            # time.sleep(2)   
            try:
                r = requests.get(url = image, verify = False) 
            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(2)
                print("Was a nice sleep, now let me continue...")
                continue  
            with open(f'{filename}', 'wb') as file:
                file.write(r.content)
        print("Saved Successfully ", response.url.split('/')[3])
        self.counter += 1
        # print(self.counter)
        if self.counter == self.MAX_CNT:
            if self.other_urls:
                self.counter = 0
                yield Request(url = self.other_urls.pop(0), callback = self.parse, dont_filter = True)
        # yield logging.info(response.url)
    
    def create_dir(self, path):
        try:
            os.makedirs(path, exist_ok = True)
            print("Created successfully")
        except OSError as error:
            print("Cannot be created")
