from pathlib import Path
import scrapy

class QuoteSpider(scrapy.Spider):
    name = 'quotes'
    
    async def start(self):
        urls =  [
            "https://quotes.toscrape.com/page/1/",
        ]
        for url in urls:
            yield scrapy.Request(url = url, callback=self.parse)
            
    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                "author": quote.xpath('.//small[@class="author"]/text()').get(),
                "text": quote.xpath('.//span[@class="text"]/text()').get(),
                "tags": quote.xpath('.//a[@class="tag"]/text()').getall()
            }
        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        
        if next_page is not None:
            yield response.follow(next_page,callback=self.parse)