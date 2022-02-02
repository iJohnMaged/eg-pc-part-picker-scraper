from urllib.parse import quote
import scrapy
from .PlaywrightSpider import PlaywrightSpider


def generate_url_with_page(url, page, is_in_stock=True):
    url_with_query_params = f"{url}?page={page}"
    if is_in_stock:
        return f"{url_with_query_params}&fq=1"
    return url_with_query_params


class ElbadrSpider(PlaywrightSpider):
    name = "ElbadrGroup"
    start_urls = dict(
        ram="https://elbadrgroupeg.store/ram",
        gpu="https://elbadrgroupeg.store/vga",
        case="https://elbadrgroupeg.store/cases",
        psu="https://elbadrgroupeg.store/power-supply",
        cooling="https://elbadrgroupeg.store/cooling",
        motherboards="https://elbadrgroupeg.store/motherboard",
        cpu="https://elbadrgroupeg.store/cpu",
        monitors="https://elbadrgroupeg.store/monitors",
        storage="https://elbadrgroupeg.store/hdd",
        accessories="https://elbadrgroupeg.store/accessories",
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
                    product.css("div.price div span::text").get()
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
