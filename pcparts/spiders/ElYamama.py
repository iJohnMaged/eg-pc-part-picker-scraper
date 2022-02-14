import urllib.parse
from .BaseSpider import BaseSpider


class ElYamamaSpider(BaseSpider):
    name = "ElYamamaSpider"
    store_name = "El Yamama Store"
    store_url = "https://elyamamastore.com"

    start_urls = dict(
        ram="https://elyamamastore.com/en/ram",
        gpu="https://elyamamastore.com/en/graphic-cards",
        case="https://elyamamastore.com/en/casesenclosures",
        psu="https://elyamamastore.com/en/powersupply",
        cooling="https://elyamamastore.com/en/hardware-accessories",
        motherboards="https://elyamamastore.com/en/motherboard-2",
        cpu="https://elyamamastore.com/en/processors",
        monitors="https://elyamamastore.com/en/displays",
        storage="https://elyamamastore.com/en/hard-drives",
        accessories="https://elyamamastore.com/en/pc-accessories-2",
    )
    query_params = dict(isFilters=1)
    page_keyword = "pageNumber"

    def has_next_page(self, response):
        pager = response.css("div.page-body div.pager")
        if pager is None:
            return False
        next_page = pager.css("li.next-page a::attr(href)").get()
        if next_page:
            return True
        return False

    def get_next_page(self, response):
        if not self.has_next_page(response):
            return False
        current_page_number = response.meta.get("page_number")
        current_category = response.meta.get("category")
        next_page_meta = response.meta.copy()
        next_page_meta.update(
            page_number=current_page_number + 1,
        )
        yield response.follow(
            self.generate_url_with_query_params(
                self.start_urls[current_category],
                current_page_number + 1,
            ),
            meta=next_page_meta,
        )

    def parse(self, response):
        for product in response.css("div.product-list div.item-box"):
            image_wrapper_tag = product.css("div.picture")
            url = urllib.parse.urljoin(
                self.store_url, image_wrapper_tag.css("a::attr(href)").get()
            )
            image = urllib.parse.urljoin(
                self.store_url, image_wrapper_tag.css("a img::attr(src)").get()
            )
            name = product.css("div.details-top h2 a::text").get()
            price = product.css("div.prices span::text").get()
            yield {
                "category": response.meta["category"],
                "url": url,
                "image": image,
                "name": name,
                "price": price,
            }

        yield from self.get_next_page(response)
