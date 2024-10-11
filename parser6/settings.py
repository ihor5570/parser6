BOT_NAME = "parser6"

SPIDER_MODULES = ["parser6.spiders"]
NEWSPIDER_MODULE = "parser6.spiders"

LOG_LEVEL = "INFO"

DOWNLOAD_DELAY = 0
CONCURENT_REQUESTS = 16

PROXY_URL = (
    "http://brd-customer-hl_5346c4a6-zone-static:hk6mkiu8efir@brd.superproxy.io:22225"
)

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
