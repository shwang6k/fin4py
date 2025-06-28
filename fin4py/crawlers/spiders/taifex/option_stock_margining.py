import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from fin4py.crawlers.utils import ItemParser


class OptionStockMarginingItem(scrapy.Item):
    Date = scrapy.Field(
        input_processor=MapCompose(
            str.strip, ItemParser.skip_cjk, ItemParser.p_date_slash
        )
    )  # 資料日期
    StockOptionSymbol = scrapy.Field()  # 股票選擇權英文代碼
    StockSymbol = scrapy.Field()  # 股票選擇權標的證券代號
    StockOptionZH = scrapy.Field()  # 股票選擇權中文簡稱
    StockZH = scrapy.Field()  # 股票選擇權標的證券
    MarginClassInterval = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.skip_cjk)
    )  # 保證金所屬級距
    SettlementMarginA = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_rate)
    )  # 結算保證金適用比例(a)
    SettlementMarginB = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_rate)
    )  # 結算保證金適用比例(b)
    MaintainMarginA = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_rate)
    )  # 維持保證金適用比例(a)
    MaintainMarginB = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_rate)
    )  # 維持保證金適用比例(b)
    InitialMarginA = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_rate)
    )  # 原始保證金適用比例(a)
    InitialMarginB = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_rate)
    )  # 原始保證金適用比例(b)

    fields_to_export = [
        "StockOptionSymbol",
        "StockSymbol",
        "StockOptionZH",
        "StockZH",
        "MarginClassInterval",
        "SettlementMarginA",
        "SettlementMarginB",
        "MaintainMarginA",
        "MaintainMarginB",
        "InitialMarginA",
        "InitialMarginB",
    ]

    @property
    def filename(self):
        return f"{self['Date'].strftime('%Y%m%d')}_stockMargining_Stock_Option.csv"


class OptionStockMarginingSpider(scrapy.Spider):
    name = "taifex_option_stock_margining"
    allowed_domains = ["www.taifex.com.tw"]
    custom_settings = {
        "ITEM_PIPELINES": {"exchanges.pipelines.CsvItemPipeline": 300},
    }
    target_dir = "/mnt/tpe-nas-l1/marketdata/info/TAIFEX/OfficialSource/Margin/"
    x_paths = [
        ("StockOptionSymbol", "//td[2]/text()"),
        ("StockSymbol", "//td[3]/text()"),
        ("StockOptionZH", "//td[4]/text()"),
        ("StockZH", "//td[5]/text()"),
        ("MarginClassInterval", "//td[6]/text()"),
        ("SettlementMarginA", "//td[7]/text()"),
        ("SettlementMarginB", "//td[8]/text()"),
        ("MaintainMarginA", "//td[10]/text()"),
        ("MaintainMarginB", "//td[11]/text()"),
        ("InitialMarginA", "//td[13]/text()"),
        ("InitialMarginB", "//td[14]/text()"),
    ]

    def start_requests(self):
        yield scrapy.Request(
            "https://www.taifex.com.tw/cht/5/stockMargining", self.parse
        )

    def parse(self, response):
        Date = response.xpath('//*[@id="printhere"]/div[1]/div/p[1]/span/text()').get()
        rows = response.xpath(
            '//*[@id="printhere"]/div[1]/div/table[1]//tr[count(td)=15]'
        ).extract()
        for row in rows:
            loader = ItemLoader(
                item=OptionStockMarginingItem(), selector=Selector(text=row)
            )
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("Date", Date)
            for field, path in self.x_paths:
                loader.add_xpath(field, path)
            yield loader.load_item()
