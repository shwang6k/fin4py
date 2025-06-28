import os
import shutil

from scrapy.exporters import CsvItemExporter

class CsvItemPipeline:
    def open_spider(self, spider):
        self.files = []
        self.exporters = {}

    def close_spider(self, spider):
        
        for exporter in self.exporters.values():
            exporter.finish_exporting()
        for file in self.files:
            file.close()
            new_path = os.path.join(spider.target_dir, file.name)
            shutil.move(file.name, new_path)
            
        
    def process_item(self, item, spider):
        exporter = self.exporters.get(item.filename)
        if not exporter:
            file = open(f'{item.filename}', 'w+b')
            exporter = CsvItemExporter(file)
            exporter.fields_to_export = item.fields_to_export
            exporter.start_exporting()
            self.files.append(file)
        exporter.export_item(item)
        self.exporters[item.filename] = exporter
        return item