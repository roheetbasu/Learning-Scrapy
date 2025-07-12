from pathlib import Path
import scrapy

class QuoteSpider(scrapy.Spider):
    name = 'quotes'
    
    async def start(self):
        url = "https://quotes.toscrape.com/"
        tag = getattr(self, "tag" , None)
        if tag is not None:
            url = url + 'tag/' + tag

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
    
class AuthorSpider(scrapy.Spider):
    name = "Author"
    
    start_urls = [
        "https://quotes.toscrape.com/",
    ]
    
    def parse(self, response):
        author_page_links = response.css('a[href^="/author"]')
        yield from response.follow_all(author_page_links,self.author_parse)
        
        yield from response.follow_all(css='li.next a', callback=self.parse)
         
    def author_parse(self, response):
        def extract_with_css(query):
            return response.css(query).get(default="").strip()
        
        yield {
            "name" : extract_with_css('h3.author-title::text'),
            "birthdate" : extract_with_css('span.author-born-date::text'),
            "birthplace" : response.css('span.author-born-location::text').get(default='').removeprefix("in ")
            
        }
        
        