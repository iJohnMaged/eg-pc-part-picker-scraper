import scrapy
from furl import furl
from pcparts.io_helper import create_folder
from pcparts import settings as pcparts_settings


class BaseSpider(scrapy.Spider):
    required_attrs = ["start_urls"]
    initial_metadata = dict(
        page_number=1,
    )
    page_keyword = "page"
    request_headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Cache-Control": "max-age=0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Sec-Fetch-Mode": "navigate",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Site": "same-origin",
    }

    def generate_url_with_query_params(self, url: str, page: int) -> str:
        base = furl(url).add({self.page_keyword: page})
        url_with_query_params = base.url
        try:
            url_with_query_params = furl(url).add(self.query_params).url
        except AttributeError:
            pass
        return url_with_query_params

    def start_requests(self):
        for category, initial_url in self.start_urls.items():
            metadata = self.initial_metadata.copy()
            metadata.update(category=category)
            if isinstance(initial_url, list):
                for url in initial_url:
                    yield scrapy.Request(
                        url=self.generate_url_with_query_params(
                            url, metadata["page_number"]
                        ),
                        meta=metadata,
                        headers=self.request_headers,
                    )
            else:
                yield scrapy.Request(
                    url=self.generate_url_with_query_params(
                        initial_url, metadata["page_number"]
                    ),
                    meta=metadata,
                    headers=self.request_headers,
                )

    def __assert_initial_values(self):
        for attr in self.required_attrs:
            assert not not getattr(
                self, attr, None
            ), f"{attr} is required in {self.name}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__assert_initial_values()
        create_folder(f"{pcparts_settings.OUTPUT_DIR}/{self.name}")
        for category, _ in self.start_urls.items():
            with open(
                f"{pcparts_settings.OUTPUT_DIR}/{self.name}/{category}.json", "w"
            ) as f:
                f.write("[]")
