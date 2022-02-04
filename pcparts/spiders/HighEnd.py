from .PlaywrightSpider import PlaywrightSpider


class HighEndSpider(PlaywrightSpider):
    name = "HighEnd"
    query_params = dict(fq=1, limit=100)
    start_urls = dict(
        cpu="https://highendstore.net/index.php?route=product/category&path=477",
        motherboards="https://highendstore.net/index.php?route=product/category&path=476",
        gpu="https://highendstore.net/index.php?route=product/category&path=475",
        memory="https://highendstore.net/index.php?route=product/category&path=472",
        storage="https://highendstore.net/index.php?route=product/category&path=482",
        monitors="https://highendstore.net/index.php?route=product/category&path=480",
        psu="https://highendstore.net/index.php?route=product/category&path=478",
        cooling="https://highendstore.net/index.php?route=product/category&path=471",
        case="https://highendstore.net/index.php?route=product/category&path=473",
    )

    async def parse(self, response):
        for product in response.css("div.main-products-wrapper div.product-layout"):
            image_container = product.css("div.image")
            image = (
                image_container.css("img")
                .attrib["srcset"]
                .split(",")[-1]
                .strip()
                .split(" ")[0]
            )
            url = image_container.css("a::attr(href)").get()
            yield {
                "category": response.meta["category"],
                "image": image,
                "name": product.css("div.name a::text").get(),
                "price": product.css("div.price div span::text").get(),
                "url": url,
            }

        end_of_products = response.css("div.ias-noneleft").get()
        # if end of products is none means we've more pages to go
        if end_of_products is None:
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
