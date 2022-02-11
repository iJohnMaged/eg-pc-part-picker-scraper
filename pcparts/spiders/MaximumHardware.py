from .JournalPaginationSpider import JournalPaginationSpider


class MaximumHardwareSpider(JournalPaginationSpider):
    name = "MaximumHardwareSpider"
    store_name = "Maximum Hardware"
    store_url = "https://www.maximumhardware.store"

    start_urls = dict(
        cpu="https://maximumhardware.store/processors",
        motherboards="https://maximumhardware.store/motherboards",
        ram="https://maximumhardware.store/memory",
        gpu="https://maximumhardware.store/graphic-card",
        storage=[
            "https://maximumhardware.store/ssd",
            "https://maximumhardware.store/hard-disks",
        ],
        cooling="https://maximumhardware.store/fans-pc-cooling",
        psu="https://maximumhardware.store/power-supply",
        case="https://maximumhardware.store/cases",
        monitors="https://maximumhardware.store/monitors",
        accessories=[
            "https://maximumhardware.store/accessories",
            "https://maximumhardware.store/headphones-speakers",
            "https://maximumhardware.store/keyboard-mouse",
        ],
    )
    query_params = dict(
        limit=100,
        mfp="stock_status[7]",
    )

    def parse(self, response):
        for product in response.css("div.products-list div.product-layout"):
            image_container = product.css("div.product-image-container")
            url = image_container.css("a::attr(href)").get()
            image = image_container.css("a img").attrib["data-src"]

            yield {
                "category": response.meta["category"],
                "image": image,
                "url": url,
                "name": product.css("h4 a::text").get(),
                "price": product.css("div.price span::text").get(),
            }

        yield from self.get_next_page(response)
