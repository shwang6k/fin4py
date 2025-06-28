import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from fin4py.crawlers.utils import ItemParser


class FutureETFMarginingItem(scrapy.Item):
    Date = scrapy.Field(
        input_processor=MapCompose(
            str.strip, ItemParser.skip_cjk, ItemParser.p_date_slash
        )
    )  # 資料日期
    StockFutureSymbol = scrapy.Field()  # 股票期貨英文代碼
    StockSymbol = scrapy.Field()  # 股票期貨標的證券代號
    StockFutureZH = scrapy.Field()  # 股票期貨中文簡稱
    StockZH = scrapy.Field()  # 股票期貨標的證券
    SettlementMargin = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 結算保證金
    MaintainMargin = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 維持保證金
    InitialMargin = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 原始保證金

    fields_to_export = [
        "StockFutureSymbol",
        "StockSymbol",
        "StockFutureZH",
        "StockZH",
        "SettlementMargin",
        "MaintainMargin",
        "InitialMargin",
    ]

    @property
    def filename(self):
        return f"{self['Date'].strftime('%Y%m%d')}_stockMargining_ETF_Future.csv"


class FutureETFMarginingSpider(scrapy.Spider):
    name = "taifex_future_etf_margining"
    allowed_domains = ["www.taifex.com.tw"]
    custom_settings = {
        "ITEM_PIPELINES": {"exchanges.pipelines.CsvItemPipeline": 300},
    }
    target_dir = "/mnt/tpe-nas-l1/marketdata/info/TAIFEX/OfficialSource/Margin/"
    x_paths = [
        ("StockFutureSymbol", "//td[2]/text()"),
        ("StockSymbol", "//td[3]/text()"),
        ("StockFutureZH", "//td[4]/text()"),
        ("StockZH", "//td[5]/text()"),
        ("SettlementMargin", "//td[6]/text()"),
        ("MaintainMargin", "//td[7]/text()"),
        ("InitialMargin", "//td[8]/text()"),
    ]

    def start_requests(self):
        yield scrapy.Request(
            "https://www.taifex.com.tw/cht/5/stockMargining", self.parse
        )

    def parse(self, response):
        Date = response.xpath('//*[@id="printhere"]/div[1]/p[4]/span/text()').get()
        rows = response.xpath(
            '//*[@id="printhere"]/div[1]/table[2]//tr[count(td)=8]'
        ).extract()
        for row in rows:
            loader = ItemLoader(
                item=FutureETFMarginingItem(), selector=Selector(text=row)
            )
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("Date", Date)
            for field, path in self.x_paths:
                loader.add_xpath(field, path)
            yield loader.load_item()
