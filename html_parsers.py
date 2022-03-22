import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


class DevbyArticleParser:
    MAX_PAGE = 750

    def get_articles_before(self, url_article):
        urls_articles = []
        for page in range(1, DevbyArticleParser.MAX_PAGE):
            urls = self.get_urls_articles_from_page(page)
            if url_article in urls:
                urls_articles.extend(urls[0: urls.index(url_article)])
                break
            else:
                urls_articles.extend(urls)
        
        return [self.get_article(url) for url in urls_articles]

    def get_articles_after(self, num_articles, url_article, start_page=1):
        for page in range(start_page, DevbyArticleParser.MAX_PAGE):
            urls = self.get_urls_articles_from_page(page)
            if url_article in urls:
                start_page = page
                break
        urls_articles = [*urls[urls.index(url_article)+1: ]]
        page = start_page + 1
        while len(urls_articles) < num_articles:
            urls_articles.extend(self.get_urls_articles_from_page(page))
            page += 1
        urls_articles = urls_articles[: num_articles]

        return [self.get_article(url) for url in urls_articles]

    def get_first_articles(self, num_articles):
        articles = []
        for page in range(1, DevbyArticleParser.MAX_PAGE):
            urls_articles = self.get_urls_articles_from_page(page)
            if len(articles) >= num_articles:
                urls_articles = urls_articles[: num_articles]
                articles = [self.get_article(url) for url in urls_articles]
                return articles

    def get_article(self, url):
        print(f'get_article {url}')
        soup = BeautifulSoup(self.get_html_doc(url), 'lxml')

        title = soup.find('h1').text
        description = soup.find_all('p')[1].text
        text = ' '.join([p.text for p in soup.find('div', class_='article__body').find_all('p')])
        date = self.to_normal_date(next(soup.find('span', id='publishedAt').stripped_strings))
        tags = []
        for span in soup.find('div', class_='article-meta_col').find_all('span'):
            if 'Теги' in span.text:
                tags = [tag.text for tag in span.find_all('a')]
                break

        return {'url': url,
                'title': title,
                'description': description,
                'text': text,
                'date': date,
                'tags': tags,}

    def get_html_doc(self, url):
        return requests.get(url).text

    def to_normal_date(self, date: str):
        MONTHS = {
            'янв': 1,
            'фев': 2,
            'мар': 3,
            'апр': 4,
            'ма': 5,
            'июн': 6,
            'июл': 7,
            'авг': 8,
            'сен': 9,
            'окт': 10,
            'ноя': 11,
            'дек': 12,
        }

        split_date = re.split('\n| |, |:', date.lower()) # '3 марта 2022, 13:31 ' -> ['3', 'марта', '2022', '13', '31', '']

        year = int(split_date[2])
        day = int(split_date[0])
        for m in MONTHS:
            if m in split_date[1]:
                month = MONTHS[m]
                break
        hour = int(split_date[3])
        minute = int(split_date[4])
        return datetime(year, month, day,hour, minute)

    def get_urls_articles_from_page(self, page):
        url_page_of_articles = 'https://devby.io/news?page={}'
        print('get links from page:',url_page_of_articles.format(page))
        doc = self.get_html_doc(url_page_of_articles.format(page))
        soup = BeautifulSoup(doc, 'lxml')

        links_to_articles = [a.get_attribute_list('href')[0] for a in soup.find_all('a', class_='card__link')]
        links_to_articles = filter(lambda x: x.startswith('/'), links_to_articles) # only relative
        links_to_articles = ['https://devby.io'+link for link in links_to_articles]
        return links_to_articles
