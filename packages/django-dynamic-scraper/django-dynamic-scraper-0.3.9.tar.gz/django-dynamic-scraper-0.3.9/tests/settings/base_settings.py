# Scrapy settings for unit tests
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ITEM_PIPELINES = [
    'dynamic_scraper.pipelines.DjangoImagesPipeline',
    'dynamic_scraper.pipelines.ValidationPipeline',
    'scraper.scraper_test.DjangoWriterPipeline',
]

IMAGES_STORE = os.path.join(PROJECT_ROOT, '../scraper/imgs')

DSCRAPER_IMAGES_STORE_FORMAT = 'FLAT'

