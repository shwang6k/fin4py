import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from fin4py.crawlers.utils import ItemParser


class StockListsItem(scrapy.Item):
    Date = scrapy.Field(
        input_processor=MapCompose(
            str.strip, ItemParser.skip_cjk, ItemParser.p_date_slash
        )
    )  # 資料日期
    SymbolPrefix = scrapy.Field()  # 股票期貨、選擇權商品代碼
    StockZH = scrapy.Field()  # 標的證券
    StockSymbol = scrapy.Field()  # 證券代號
    StockAbbreviationZH = scrapy.Field()  # 標的證券簡稱
    HasStockFuture = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_circle_sign)
    )  # 是否為股票期貨標的
    HasStockOption = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_circle_sign)
    )  # 是否為股票選擇權標的
    IsETStock = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_circle_sign)
    )  # 上市普通股標的證券
    IsOTCStock = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_circle_sign)
    )  # 上櫃普通股標的證券
    IsETETF = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_circle_sign)
    )  # 上市ETF標的證券
    NotionalFactor = scrapy.Field()  # 標準型證券股數

    fields_to_export = [
        "SymbolPrefix",
        "StockZH",
        "StockSymbol",
        "StockAbbreviationZH",
        "HasStockFuture",
        "HasStockOption",
        "IsETStock",
        "IsOTCStock",
        "IsETETF",
        "NotionalFactor",
    ]

    @property
    def filename(self):
        return f"{self['Date'].strftime('%Y%m%d')}_TAXFEX_stockLists.csv"


class StockListsSpider(scrapy.Spider):
    name = "taifex_stock_lists"
    allowed_domains = ["www.taifex.com.tw"]
    custom_settings = {
        "ITEM_PIPELINES": {"exchanges.pipelines.CsvItemPipeline": 300},
    }
    target_dir = "/mnt/tpe-nas-l1/marketdata/info/TAIFEX/OfficialSource/stockLists/"
    x_paths = [
        ("SymbolPrefix", "//td[1]/text()"),
        ("StockZH", "//td[2]/text()"),
        ("StockSymbol", "//td[3]/text()"),
        ("StockAbbreviationZH", "//td[4]/text()"),
        ("HasStockFuture", "//td[5]/font/text()"),
        ("HasStockOption", "//td[6]/font/text()"),
        ("IsETStock", "//td[7]/font/text()"),
        ("IsOTCStock", "//td[8]/font/text()"),
        ("IsETETF", "//td[9]/font/text()"),
        ("NotionalFactor", "//td[10]/text()"),
    ]

    def start_requests(self):
        yield scrapy.Request("https://www.taifex.com.tw/cht/2/stockLists", self.parse)

    def parse(self, response):
        rows = response.xpath("//tr[count(td)=10]").extract()
        Date = response.xpath("/html/body/div[2]/div/div/div/div[2]/p[1]/text()").get()
        Date = Date.replace("年", "/").replace("月", "/")
        for row in rows:
            loader = ItemLoader(item=StockListsItem(), selector=Selector(text=row))
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("Date", Date)
            for field, path in self.x_paths:
                loader.add_xpath(field, path)
            yield loader.load_item()
