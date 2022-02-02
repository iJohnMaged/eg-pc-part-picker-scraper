from urllib.parse import quote
import scrapy
from .PlaywrightSpider import PlaywrightSpider


def generate_url_with_page(url, page, is_in_stock=True):
    url_with_query_params = f"{url}?page={page}"
    if is_in_stock:
        return f"{url_with_query_params}&fq=1"
    return url_with_query_params


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

    def start_requests(self):
        for category, initial_url in self.start_urls.items():
            metadata = self.initial_metadata.copy()
            metadata.update(category=category)
            yield scrapy.Request(
                generate_url_with_page(initial_url, metadata["page_number"]),
                meta=metadata,
            )

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
            current_is_in_stock = response.meta.get("is_in_stock")
            next_page_meta = response.meta.copy()
            next_page_meta.update(
                page_number=current_page_number + 1,
            )
            yield response.follow(
                generate_url_with_page(
                    self.start_urls[current_category],
                    current_page_number + 1,
                    is_in_stock=current_is_in_stock,
                ),
                meta=next_page_meta,
            )
