# Scrapy settings for thurnage project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'thurnage'

SPIDER_MODULES = ['thurnage.spiders']
NEWSPIDER_MODULE = 'thurnage.spiders'

ITEM_PIPELINES = {
    'thurnage.pipelines.ThurneNamePipeline': 300,
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'thurnage (+http://www.yourdomain.com)'
