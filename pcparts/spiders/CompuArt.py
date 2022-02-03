from urllib.parse import quote
import scrapy
from .PlaywrightSpider import PlaywrightSpider


class CompuartSpider(PlaywrightSpider):
    name = "CompuArt"
    start_urls = dict(
        ram="https://www.compuartstore.com/core-components/memory",
        gpu="https://www.compuartstore.com/core-components/video-cards",
        case="https://www.compuartstore.com/core-components/computer-cases",
        psu="https://www.compuartstore.com/core-components/power-supplies",
        cooling="https://www.compuartstore.com/core-components/fans-pc-cooling",
        motherboards="https://www.compuartstore.com/core-components/motherboards",
        cpu="https://www.compuartstore.com/core-components/cpus-processor",
        monitors="https://www.compuartstore.com/monitors",
        storage="https://www.compuartstore.com/storage-devices",
        accessories="https://www.compuartstore.com/computer-accessories",
    )
    # Fq is query param for in-stock products
    query_params = dict(fq=1)

    def encode_url(self, url):
        return quote(url, safe="/:?=&")

    def parse_price_float(self, price_str):
        if price_str is None:
            return 0
        return float(price_str.replace("EGP", "").replace(",", "").strip())

    async def parse(self, response):
        for product in response.css(
            "div.main-products.product-grid div.product-layout"
        ):
            image_main_tag = product.css("a.product-img img")
            yield {
                "category": response.meta["category"],
                "image": self.encode_url(
                    image_main_tag.attrib.get(
                        "srcset", image_main_tag.attrib.get("data-srcset")
                    )
                    .split(",")[-1]
                    .strip()
                    .split(" ")[0]
                ),
                "name": product.css("div.name a::text").get(),
                "price": self.parse_price_float(
                    product.css("div.price span::text").get()
                ),
                "url": self.encode_url(product.css("div.name a::attr(href)").get()),
            }
        end_of_products = response.css("div.ias-noneleft").get()
        if end_of_products is not None:
            current_page_number = response.meta.get("page_number")
            current_category = response.meta.get("category")
            next_page_meta = response.meta.copy()
            next_page_meta.update(
                page_number=current_page_number + 1,
            )
            yield response.follow(
                self.__generate_url_with_query_params(
                    self.start_urls[current_category],
                    current_page_number + 1,
                ),
                meta=next_page_meta,
            )
