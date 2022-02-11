from .BaseSpider import BaseSpider

class JournalPaginationSpider(BaseSpider):
    cookies = {}
    
    def has_next_page(self, response):
        pagination = response.css("ul.pagination")
        if pagination:
            next_page = pagination.xpath(
                '//li[@class="active"]/following-sibling::li/a/@href'
            ).get()
            if next_page:
                return True
        return False
    

    def get_next_page(self, response):
        if not self.has_next_page(response):
            return None
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
            cookies=self.cookies,
        )
