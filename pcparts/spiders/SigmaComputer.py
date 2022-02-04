from .PlaywrightSpider import PlaywrightSpider
import scrapy
from http.cookies import SimpleCookie
import urllib.parse


class SigmaComputerSpider(PlaywrightSpider):
    name = "SigmaComputerSpider"
    store_name = "Sigma Computer"
    store_url = "https://www.sigma-computer.com"

    base_url = "https://www.sigma-computer.com"
    start_urls = dict(
        motherbaords="https://www.sigma-computer.com/subcategory?id=1&cname=Desktop&id2=1&scname=Motherboard",
        gpu="https://www.sigma-computer.com/subcategory?id=1&cname=Desktop&id2=2&scname=Graphic%20Card",
        ram="https://www.sigma-computer.com/subcategory?id=1&cname=Desktop&id2=3&scname=Ram",
        cpu="https://www.sigma-computer.com/subcategory?id=1&cname=Desktop&id2=4&scname=Processors",
        case="https://www.sigma-computer.com/subcategory?id=1&cname=Desktop&id2=29&scname=Computer%20Case",
        psu="https://www.sigma-computer.com/subcategory?id=1&cname=Desktop&id2=61&scname=Power%20Supply",
        monitors="https://www.sigma-computer.com/category?id=4&cname=Monitors",
        cooling="https://www.sigma-computer.com/subcategory?id=6&cname=Accessories&id2=11&scname=PC%20Cooling",
        storage="https://www.sigma-computer.com/subcategory?id=3&cname=Storage&id2=7&scname=SSD",
    )
    set_in_stock_url = "https://www.sigma-computer.com/setout_of_stock?set_con=close"
    cookies = {}

    def start_requests(self):
        # Get cookies by setting items to be in stock only
        yield scrapy.Request(
            self.set_in_stock_url, callback=self.start_requests_with_cookies
        )

    def start_requests_with_cookies(self, response):
        response_cookies = response.headers.getlist("Set-Cookie")
        for cookie_bytes in response_cookies:
            cookie_str = cookie_bytes.decode("utf-8")
            cookie = SimpleCookie(cookie_str)
            for key, morsel in cookie.items():
                self.cookies[key] = morsel.value

        for category, initial_url in self.start_urls.items():
            metadata = self.initial_metadata.copy()
            metadata.update(category=category)
            yield scrapy.Request(
                self.generate_url_with_query_params(
                    initial_url, metadata["page_number"]
                ),
                cookies=self.cookies,
                meta=metadata,
                callback=self.parse,
            )

    async def parse(self, response):
        for product in response.css("div.products-list div.product-layout"):
            image_container = product.css("div.product-image-container")
            image = urllib.parse.urljoin(
                self.base_url, image_container.css("a img::attr(src)").get()
            )
            url = urllib.parse.urljoin(
                self.base_url, image_container.css("a::attr(href)").get()
            )

            yield {
                "category": response.meta["category"],
                "image": image,
                "url": url,
                "name": product.css("div.caption h4 a::text").get(),
                "price": product.css("p.price span::text").get(),
            }

        pagination = response.css("ul.pagination")

        if pagination is not None:
            next_page_url = pagination.xpath(
                "//ul[@class='pagination']/li/a[@rel='next']/@href"
            ).get()
            if next_page_url is not None:
                metadata = response.meta.copy()
                metadata.update(page_number=metadata["page_number"] + 1)
                yield response.follow(
                    next_page_url,
                    meta=metadata,
                    cookies=self.cookies,
                )
