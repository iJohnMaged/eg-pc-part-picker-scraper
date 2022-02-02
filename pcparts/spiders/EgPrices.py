import scrapy
from .PlaywrightSpider import PlaywrightSpider


def generate_url_with_page(url, page, is_in_stock=True):
    url_with_query_params = f"{url}?page={page}"
    if is_in_stock:
        return f"{url_with_query_params}&stock=yes"
    return url_with_query_params


class EgpricesSpider(PlaywrightSpider):
    name = "EgPrices"
    start_urls = dict(
        cooling="https://www.egprices.com/en/category/computers/computer-components-hardware/fans-cooling-systems",
        ram="https://www.egprices.com/en/category/computers/components/memory/desktop",
        case="https://www.egprices.com/en/category/computers/components/cases",
        accessories="https://www.egprices.com/en/category/computers/computer-components-hardware/accessories",
        storage="https://www.egprices.com/en/category/computers/storage",
        gpu="https://www.egprices.com/en/category/computers/computer-components-hardware/graphics-cards",
        motherboards="https://www.egprices.com/en/category/computers/computer-components-hardware/motherboards",
        cpu="https://www.egprices.com/en/category/computers/components/processors",
        psu="https://www.egprices.com/en/category/computers/components/power-supplies",
        monitors="https://www.egprices.com/en/category/computers/computer-monitors",
    )

    def start_requests(self):
        for category, initial_url in self.start_urls.items():
            metadata = self.initial_metadata.copy()
            metadata.update(category=category)
            yield scrapy.Request(
                generate_url_with_page(initial_url, metadata["page_number"]),
                meta=metadata,
            )

    def parse_price_float(self, price_str):
        if not price_str:
            return 0
        return float(price_str.replace("EGP", "").replace(",", "").strip())

    def parse_product_image(self, product):
        image = product.css(
            "div.text-center.align-self-top.small-3.medium-2.columns img::attr(src)"
        ).get()
        if image is None:
            return ""
        return image.replace("thumb", "large")

    async def parse(self, response):
        for product in response.css(
            'div.row.align-middle.collapse[style="min-height:80px"]'
        ):
            print(
                "something", product.css("div.small-9.medium-7.columns div::text").get()
            )
            yield {
                "name": product.css("div.small-9.medium-7.columns div::text").get(),
                "price": self.parse_price_float(
                    product.css(
                        "div.small-6.medium-12.text-left.medium-text-center.columns::text"
                    ).get()
                ),
                "image": self.parse_product_image(product),
                "url": response.urljoin(
                    product.css("div.small-9.medium-7.columns a::attr(href)").get()
                ),
                "category": response.meta["category"],
            }

        next_page = response.xpath(
            "//i[@class='fa fa-angle-double-right']/../@href"
        ).get()

        if next_page is not None:
            metadata = response.meta.copy()
            metadata.update(page_number=metadata["page_number"] + 1)
            yield response.follow(
                response.urljoin(next_page),
                meta=metadata,
            )
