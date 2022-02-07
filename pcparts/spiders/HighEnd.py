from .JournalPaginationSpider import JournalPaginationSpider


class HighEndSpider(JournalPaginationSpider):
    name = "HighEndSpider"
    store_name = "High End"
    store_url = "https://highendstore.net"

    query_params = dict(fq=1, limit=100)
    start_urls = dict(
        cpu="https://highendstore.net/index.php?route=product/category&path=477",
        motherboards="https://highendstore.net/index.php?route=product/category&path=476",
        gpu="https://highendstore.net/index.php?route=product/category&path=475",
        ram="https://highendstore.net/index.php?route=product/category&path=472",
        monitors="https://highendstore.net/index.php?route=product/category&path=480",
        psu="https://highendstore.net/index.php?route=product/category&path=478",
        cooling="https://highendstore.net/index.php?route=product/category&path=471",
        case="https://highendstore.net/index.php?route=product/category&path=473",
        storage=[
            "https://highendstore.net/index.php?route=product/category&path=482",
            "https://highendstore.net/index.php?route=product/category&path=481",
        ],
        accessories=[
            "https://highendstore.net/index.php?route=product/category&path=484",
            "https://highendstore.net/index.php?route=product/category&path=474",
            "https://highendstore.net/index.php?route=product/category&path=479",
            "https://highendstore.net/index.php?route=product/category&path=485",
        ],
    )

    def parse(self, response):
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

        yield from self.get_next_page(response)
