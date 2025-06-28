import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from fin4py.crawlers.utils import ItemParser


class OptionETFMarginingItem(scrapy.Item):
    Date = scrapy.Field(
        input_processor=MapCompose(
            str.strip, ItemParser.skip_cjk, ItemParser.p_date_slash
        )
    )  # 資料日期
    StockOptionSymbol = scrapy.Field()  # 股票選擇權英文代碼
    StockSymbol = scrapy.Field()  # 股票選擇權標的證券代號
    StockOptionZH = scrapy.Field()  # 股票選擇權中文簡稱
    StockZH = scrapy.Field()  # 股票選擇權標的證券
    SettlementMarginA = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 結算保證金(A)
    SettlementMarginB = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 結算保證金(B)
    MaintainMarginA = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 維持保證金(A)
    MaintainMarginB = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 維持保證金(B)
    InitialMarginA = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 原始保證金(A)
    InitialMarginB = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num)
    )  # 原始保證金(B)

    fields_to_export = [
        "StockOptionSymbol",
        "StockSymbol",
        "StockOptionZH",
        "StockZH",
        "SettlementMarginA",
        "SettlementMarginB",
        "MaintainMarginA",
        "MaintainMarginB",
        "InitialMarginA",
        "InitialMarginB",
    ]

    @property
    def filename(self):
        return f"{self['Date'].strftime('%Y%m%d')}_stockMargining_ETF_Option.csv"


class OptionETFMarginingSpider(scrapy.Spider):
    name = "taifex_option_etf_margining"
    allowed_domains = ["www.taifex.com.tw"]
    custom_settings = {
        "ITEM_PIPELINES": {"exchanges.pipelines.CsvItemPipeline": 300},
    }
    target_dir = "/mnt/tpe-nas-l1/marketdata/info/TAIFEX/OfficialSource/Margin/"
    row1_x_paths = [
        ("StockOptionSymbol", "//td[2]/text()"),
        ("StockSymbol", "//td[3]/text()"),
        ("StockOptionZH", "//td[4]/text()"),
        ("StockZH", "//td[5]/text()"),
        ("SettlementMarginA", "//td[7]/text()"),
        ("MaintainMarginA", "//td[8]/text()"),
        ("InitialMarginA", "//td[9]/text()"),
    ]

    row2_x_paths = [
        ("SettlementMarginB", "//td[2]/text()"),
        ("MaintainMarginB", "//td[3]/text()"),
        ("InitialMarginB", "//td[4]/text()"),
    ]

    def start_requests(self):
        yield scrapy.Request(
            "https://www.taifex.com.tw/cht/5/stockMargining", self.parse
        )

    def parse(self, response):
        Date = response.xpath('//*[@id="printhere"]/div[1]/div/p[5]/span/text()').get()
        rows = response.xpath(
            '//*[@id="printhere"]/div[1]/div/table[2]//tr[count(td)>1]'
        ).extract()

        for row1, row2 in self._pairwise(rows):
            loader = ItemLoader(
                item=OptionETFMarginingItem(), selector=Selector(text=row1)
            )
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("Date", Date)

            selector1 = Selector(text=row1)
            for field, path in self.row1_x_paths:
                value = selector1.xpath(path).get()
                loader.add_value(field, value)

            selector2 = Selector(text=row2)
            for field, path in self.row2_x_paths:
                value = selector2.xpath(path).get()
                loader.add_value(field, value)

            yield loader.load_item()

    @classmethod
    def _pairwise(cls, iterable):
        a = iter(iterable)
        return zip(a, a)
