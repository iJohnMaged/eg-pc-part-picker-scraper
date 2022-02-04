from .PlaywrightSpider import PlaywrightSpider


class ElBadrGroupSpider(PlaywrightSpider):
    name = "ElBadrGroupSpider"
    store_name = "El Badr Group"
    store_url = "https://elbadrgroupeg.store"

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
    query_params = dict(fq=1)

    async def parse(self, response):
        for product in response.css(
            "div.main-products.product-grid div.product-layout"
        ):
            image_main_tag = product.css("a.product-img img")
            yield {
                "category": response.meta["category"],
                "image": image_main_tag.attrib.get(
                    "srcset", image_main_tag.attrib.get("data-srcset")
                )
                .split(",")[-1]
                .strip()
                .split(" ")[0],
                "name": product.css("div.name a::text").get(),
                "price": product.css("div.price div span::text").get(),
                "url": product.css("div.name a::attr(href)").get(),
            }
        end_of_products = response.css("div.ias-noneleft").get()

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
