import requests
from bs4 import BeautifulSoup
import nltk.corpus
import re
from datetime import datetime

def get_html_doc(url):
    return requests.get(url).text

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
def to_normal_date(date: str):
    split_date = re.split('\n| |, |:', date.lower()) # '3 марта 2022, 13:31 ' -> ['3', 'марта', '2022', '13', '31', '']

    year = int(split_date[2])
    day = int(split_date[0])
    for m in MONTHS:
        if m in split_date[1]:
            month = MONTHS[m]
    hour = int(split_date[3])
    minute = int(split_date[4])
    return datetime(year, month, day,hour, minute)


def delete_xa0(text):
    return text.replace(u'\xa0', u' ')


def get_article(url):
    print(f'get_article {url}')
    soup = BeautifulSoup(get_html_doc(url), 'lxml')

    title = soup.find('h1').text
    description = soup.find_all('p')[1].text
    text = ' '.join([p.text for p in soup.find('div', class_='article__body').find_all('p')])
    date = to_normal_date(next(soup.find('span', id='publishedAt').stripped_strings))
    tags = []
    for span in soup.find('div', class_='article-meta_col').find_all('span'):
        if 'Теги' in span.text:
            tags = [tag.text for tag in span.find_all('a')]
            break
    emotions = []

    return {'url': url,
            'title': title,
            'description': description,
            'text': text,
            'date': date,
            'tags': tags,
            'emotions': emotions}
    

def get_articles_from_pages(pages: list):
    articles = []

    url_page_of_articles = 'https://devby.io/news?page={}'
    for page in pages:
        doc = get_html_doc(url_page_of_articles.format(page))
        soup = BeautifulSoup(doc, 'lxml')
        links_to_articles = [a.get_attribute_list('href')[0] for a in soup.find_all('a', class_='card__link')]
        links_to_articles = filter(lambda x: x.startswith('/'), links_to_articles)
        for link in links_to_articles:
            url = 'https://devby.io' + link
            articles.append(get_article(url))
    return articles
