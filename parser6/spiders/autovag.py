import re
from datetime import datetime
from typing import Any

import scrapy

from utils.xlsx import XlsxReader


class AutovagSpider(scrapy.Spider):
    name = "autovag"
    allowed_domains = ["autovag.com.ua"]
    start_urls = ["http://autovag.com.ua"]

    current_date = datetime.now()

    custom_settings = {
        "FEED_URI": f'data/{name}_{current_date.strftime("%Y-%m-%d_%H%M")}-6.xlsx',
        "FEED_FORMAT": "xlsx",
        "FEED_EXPORTERS": {
            "xlsx": "scrapy_xlsx.XlsxItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def __init__(self, name: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.keywords = XlsxReader.get_input_data_from_xlsx()

    def parse(self, response):
        for index, keyword in enumerate(self.keywords.keys(), 1):
            yield scrapy.FormRequest(
                "http://autovag.com.ua/search",
                formdata={
                    "words": keyword,
                },
                callback=self.parse_products,
                cb_kwargs={"keyword": keyword, "index": index},
            )

    def parse_products(self, response, keyword, index):
        product_lists = response.css(".list_table")
        if not product_lists:
            self.logger.info("Item[%s] Keyword %s is not in stock" % (index, keyword))
            return

        product_list = product_lists[0]
        products = product_list.css("tr")
        products.pop(0)

        for product in products:
            product = product.get()

            if (
                re.search(rf"\b{re.escape(keyword)}\b", product)
                and "Под заказ" not in product
            ):
                self.logger.info("Item[%s] Keyword %s is in stock" % (index, keyword))
                return {
                    "Производитель": self.keywords[keyword],
                    "Код": keyword,
                    "Наличие": "В наличии",
                }

        self.logger.info("Item[%s] Keyword %s is not in stock" % (index, keyword))
