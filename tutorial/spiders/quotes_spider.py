from pathlib import Path
import scrapy
import json

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
    # shortcut for async def start
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
        
class QuoteSpiderScroll(scrapy.Spider):
    name = "quote"
    allowed_domains = ["quotes.toscrape.com"]
    page = 1
    start_urls = ["https://quotes.toscrape.com/api/quotes?page=1"]
    
    def parse(self, response):
        data = json.load(response.text)
        
        for quote in data["quotes"]:
            yield {"quotes":quote['text']}
            
        if data["has_next"]:
            self.page += 1
            url = f'https://quotes.toscrape.com/api/quotes?page={self.page}'
            yield scrapy.Request(url=url, callback = self.parse)
            
request = scrapy.Request.from_curl("""
   curl 'https://quotes.toscrape.com/api/quotes?page=1' \
  -H 'accept: */*' \
  -H 'accept-language: en-GB,en;q=0.5' \
  -H 'priority: u=1, i' \
  -H 'referer: https://quotes.toscrape.com/scroll' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36' \
  -H 'x-requested-with: XMLHttpRequest'
  """
)