from .PlaywrightSpider import PlaywrightSpider


class MaximumHardwareSpider(PlaywrightSpider):
    name = "MaximumHardware"
    start_urls = dict(
        cpu="https://maximumhardware.store/processors",
        motherboards="https://maximumhardware.store/motherboards",
        ram="https://maximumhardware.store/memory",
        gpu="https://maximumhardware.store/graphic-card",
        storage="https://maximumhardware.store/ssd",
        cooling="https://maximumhardware.store/fans-pc-cooling",
        psu="https://maximumhardware.store/power-supply",
        case="https://maximumhardware.store/cases",
        monitors="https://maximumhardware.store/monitors",
        accessories="https://maximumhardware.store/accessories",
    )
    query_params = dict(
        limit=100,
        mfp="stock_status[7]",
    )

    async def parse(self, response):
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

        pagination = response.css("ul.pagination").get()
        if pagination:
            next_page = pagination.xpath(
                '//li[@class="active"]/following-sibling::li/a/@href'
            ).get()
            if next_page:
                metadata = response.meta.copy()
                metadata.update(page_number=metadata["page_number"] + 1)
                yield response.follow(
                    self.generate_url_with_query_params(
                        next_page, metadata["page_number"]
                    ),
                    meta=metadata,
                )
