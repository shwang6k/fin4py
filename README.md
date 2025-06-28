

股市技術分析小工具
======================
> **This project is no longer maintained.**

[![PyPI](https://img.shields.io/badge/pipy-v0.2.2-green.svg)](https://pypi.python.org/pypi/finance4py)
[![MIT](https://img.shields.io/github/license/shwang-bk/finance4py)](https://opensource.org/licenses/MIT)



對於目前在python好像還沒找到一個適合作為股市技術分析的套件，所以決定先刻一份簡單的工具頂著用。   
* 新增簡易的波段回測投報率線圖，參考自[幣圖誌](http://www.bituzi.com/2014/12/Rbacktest6mins.html)    
* 新增取得三大法人賣賣超功能(測試)

![範例快照](example_screenshot.png)


使用說明
======================
* 使用 uv 下載相依套件
  ```sh
  uv sync
  ```

* 基本技術線圖的取得請參考範例程式 example.py
  ```sh
  uv run python example.py
  ```

* 回測程式部分可自行定義以下函式處理自己的策略並交給回測程式處理即可
  ```python
  def strategy(today, today_data, stock):
      return
  ```
  詳情請參考範例程式 example_backtesting.py
  ```sh
  uv run python example_backtesting.py   
  ```
  
* 爬蟲列表
  ```sh
  $ pipenv run scrapy list
  taifex_future_code  # 期貨對應碼
  twse_stock_basic    # 上市公司基本資訊
  twse_stock_branch   # 券商分點
  twse_stock_chip     # 三大法人
  twse_stock_margin   # 資券餘額
  twse_stock_quote    # 交易概況
  twse_warrant_info   # 權證資訊
  ```

* 爬取資料
  ```sh
  $ pipenv run scrapy crawl twse_stock_quote -a date=20200325 -o quote_20200325.csv
  ```
