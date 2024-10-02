# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from douban.items import ActorItem, ReviewItem


class DoubanPipeline:

    def __init__(self):
        self.actor_file = None
        self.review_file = None

    def open_spider(self, spider):
        self.actor_file = open('./actor.txt', 'w', encoding='utf-8')
        self.review_file = open('./review.txt', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if isinstance(item, ActorItem):
            actor = adapter['actor']
            role = adapter['role']
            span1 = adapter['span1']
            span2 = adapter['span2']
            self.actor_file.write(actor + ' ' + role + '\n\t'+span1+'\n\t'+span2+'\n')

        elif isinstance(item, ReviewItem):
            idname = adapter['idname']
            title = adapter['title']
            shortcontent = adapter['shortcontent']
            self.review_file.write(idname + '\n\t' + title + '\n\t' + shortcontent + '\n\n')

    def close_spider(self, spider):
        if self.actor_file:
            self.actor_file.close()
        elif self.review_file:
            self.review_file.close()