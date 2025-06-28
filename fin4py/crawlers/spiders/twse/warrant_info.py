import datetime
import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst
from fin4py.crawlers.utils import ItemParser


class WarrantInfoItem(scrapy.Item):
    date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date)
    )  # 資料日期
    code = scrapy.Field()  # 權證代號
    name = scrapy.Field()  # 權證簡稱
    style = scrapy.Field(input_processor=MapCompose(ItemParser.p_style))  # 美式/歐式
    put_call = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_put_call)
    )  # 認購/認售
    broker = scrapy.Field()  # 發行人
    price = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float)
    )  # 權證收盤價格
    listing_date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date_minguo)
    )  # 上市日期
    close_date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date_minguo)
    )  # 最後交易日
    delivery_date = scrapy.Field(
        input_processor=MapCompose(str.strip, ItemParser.p_date_minguo)
    )  # 到期日
    publish_shares = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, int)
    )  # 權證發行數量
    underlying = scrapy.Field()  # 標的代號
    underlying_price = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float)
    )  # 標的收盤價格/收盤指數/期貨結算價
    exercise_ratio = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float, lambda x: x / float(1000.0))
    )  # 行使比例
    strike_price = scrapy.Field(
        input_processor=MapCompose(ItemParser.p_num, float)
    )  # 最新履約價格

    class Meta:
        fields = [
            "code",
            "name",
            "style",
            "put_call",
            "broker",
            None,
            "price",
            "listing_date",
            "close_date",
            "delivery_date",
            None,
            "publish_shares",
            "underlying",
            None,
            "underlying_price",
            "exercise_ratio",
            "strike_price",
        ]


class WarrantInfoSpider(scrapy.Spider):
    name = "twse_warrant_info"
    allowed_domains = ["isin.twse.com.tw"]
    date = datetime.date.today().strftime("%Y%m%d")

    def start_requests(self):
        self.logger.info(f"Parsing date: {self.date}")
        yield scrapy.FormRequest(
            url="https://mops.twse.com.tw/mops/web/ajax_t90sbfa01",
            formdata={
                "encodeURIComponent": "1",
                "step": "1",
                "ver": "1.9",
                "TYPEK": "",
                "market": "1",
                "wrn_class": "all",
                "stock_no": "",
                "wrn_no": "",
                "co_id": "all",
                "wrn_type": "all",
                "left_month": "all",
                "return_rate": "all",
                "price_down": "",
                "price_up": "",
                "price_inout": "all",
                "newprice_down": "",
                "newprice_up": "",
                "fin_down": "",
                "fin_up": "",
                "sort": "1",
            },
            callback=self.parse,
        )

    def parse(self, response):
        self.logger.info("%s", response.url)
        fields = WarrantInfoItem.Meta.fields
        rows = response.xpath("//tr[count(td)=21]").extract()
        for row in rows:
            loader = ItemLoader(item=WarrantInfoItem(), selector=Selector(text=row))
            loader.default_input_processor = MapCompose(str, str.strip)
            loader.default_output_processor = TakeFirst()
            loader.add_value("date", self.date)
            for idx, field in enumerate(fields, start=1):
                if field:
                    loader.add_xpath(field, f"//td[{idx}]/text()")
            yield loader.load_item()
