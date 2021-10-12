import argparse
import logging
import re

from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

from requests.models import HTTPError

import news_page_objects as news

from common import config
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)
is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')


def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info('Begining scraper for {}'.format(host))
    homepage = news.HomePage(news_site_uid, host)
    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_uid, host, link)

        if article:
            logger.info('Article fetched')
            articles.append(article)
            print(article.title)

    print(len(articles))


def _fetch_article(news_site_uid, host, link):
    logger.info('Start fetching article at {}'.format(link))

    article = None
    try:
        article = news.ArticlePage(news_site_uid, _build_link(host, link))

    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetchin', exc_info=False)
        pass

    if article and not article.body:
        logger.warning('Invalid article. There is not body')
        return None

    return article


def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return '{}{}'.format(host, link)
    else:
        return '{host}/{uri}'.format(host=host, uri=link)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    new_sites_choises = list(config()['news_sites'].keys())

    parser.add_argument(
        'new_site', help='The news site that you want to scrape', type=str, choices=new_sites_choises)

    args = parser.parse_args()

    _news_scraper(args.new_site)
