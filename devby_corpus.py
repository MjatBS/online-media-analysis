from datetime import datetime
import os.path
import json


class ArticleCorpus:
    '''
    corpuses
        corpus_name
            METADATA
            README.md
            articles
                2022-03-15_09:37:00.json
                2022-03-14_16:45:00.json
                2022-03-14_14:12:00.json
    '''

    def __init__(self, corpus_name, html_article_parser):
        self.corpus_path = f'corpuses/{corpus_name}'
        self.metadata_path = f'{self.corpus_path}/METADATA'
        self.readme_path = f'{self.corpus_path}/README.md'
        self.articles_path = f'{self.corpus_path}/articles'

        self.html_article_parser = html_article_parser()
        self.corpus_io = CorpusIO()
        self.metadata = Metadata(self.metadata_path, CorpusIO())


    def create_new_corpus(self, descr, num_articles=1):
        corpus_io = self.corpus_io
        corpus_io.create_dirs(self.corpus_path)
        corpus_io.write_file(self.metadata_path, '')
        corpus_io.write_file(self.readme_path, descr)
        corpus_io.create_dirs(self.articles_path)

        num_articles = 1 if num_articles < 1 else num_articles
        articles = self.html_article_parser.get_first_articles(num_articles)
        
        articles = sorted(articles, key=lambda a: a['date'], reverse=True)
        metadata = {
            'last_updated': datetime.now(),
            'from_date': articles[0]['date'],
            'from_article': articles[0]['url'],
            'to_date': articles[-1]['date'],
            'to_article': articles[-1]['url']     
        }
        self.metadata.write_fields(metadata)
        self._write_articles(articles)

    
    def get_all_articles(self):
        article_names = self.corpus_io.ls(self.articles_path)
        article_names = [f'{self.articles_path}/{name}' for name in article_names]
        return (self.corpus_io.read_article(name) for name in article_names)

    
    def update_with_new_articles(self):
        url = self.metadata.read_fields()['from_article']
        articles = self.html_article_parser.get_articles_before(url)
        self._update_with_articles(articles)

    def download_old_articles(self, num_articles):
        url = self.metadata.read_fields()['to_article']
        articles = self.html_article_parser.get_articles_after(num_articles, url)
        self._update_with_articles(articles)


    def _update_with_articles(self, articles: list):
        articles = sorted(articles, key=lambda a: a['date'], reverse=True)
        self._update_metadata(articles)
        self._write_articles(articles)
        
    def _update_metadata(self, articles):
        metadata = self.metadata.read_fields()
        if articles[0]['date'] > metadata['from_date']:
            metadata['from_date'] = articles[0]['date']
            metadata['from_article'] = articles[0]['url']
        if articles[-1]['date'] < metadata['to_date']:
            metadata['to_date'] = articles[-1]['date']
            metadata['to_article'] = articles[-1]['url']
        metadata['last_updated'] = datetime.now()
        self.metadata.write_fields(metadata)

    def _write_articles(self, articles: list):
        for article in articles:
            article_name = DateToStr.date_to_str(article['date'])
            article_path = f'{self.articles_path}/{article_name}.json'
            self.corpus_io.write_article(article_path, article)

    
    


class Metadata:
    '''
    fields:
    last_updated - date of last update
    from_date - corpus has articles from date
    to_date - corpus has article to date
    from_article - url of first article
    to_article - url of last article
    '''

    def __init__(self, metadata_path, metadata_io):
        self.path = metadata_path
        self.metadata_io = metadata_io

    def read_fields(self) -> dict:
        raw_metadata = self.metadata_io.read_file(self.path)
        lines = raw_metadata.split('\n')
        fields = {}
        for line in lines:
            i_sep = line.index('=')
            fields[line[0: i_sep]] = line[i_sep+1: ]
        fields['last_updated'] = DateToStr.str_to_date(fields['last_updated'])
        fields['from_date'] = DateToStr.str_to_date(fields['from_date'])
        fields['to_date'] = DateToStr.str_to_date(fields['to_date'])
        return fields

    def write_fields(self, fields: dict):
        fields['last_updated'] = DateToStr.date_to_str(fields['last_updated'])
        fields['from_date'] = DateToStr.date_to_str(fields['from_date'])
        fields['to_date'] = DateToStr.date_to_str(fields['to_date'])
        field_value = [f'{field}={value}' for field, value in fields.items()]
        metadata = '\n'.join(field_value)
        self.metadata_io.write_file(self.path, metadata)


import os
import json

class CorpusIO:
    '''
    separator in path must be '/': example/work/so_on.txt
    Use json format for articles
    '''

    def is_exists(self, path):
        path.replace('/', os.path.sep)
        return os.path.exists(path)
    
    def create_dirs(self, path):
        path.replace('/', os.path.sep)
        if not os.path.exists(path):
            os.makedirs(path)

    def write_file(self, path, text):
        path.replace('/', os.path.sep)
        with open(path, 'w') as destination:
            destination.write(text)

    def read_file(self, path):
        path.replace('/', os.path.sep)
        with open(path, 'r') as source:
            text = source.read()
        return text

    def ls(self, path):
        return os.listdir(path)

    def write_article(self, path, article):
        path.replace('/', os.path.sep)
        with open(path, 'w', encoding='utf8') as destination:
            json.dump(
                article, 
                destination, 
                default=CorpusIO.encode_date, 
                ensure_ascii=False)

    def read_article(self, path):
        path.replace('/', os.path.sep)
        with open(path, 'r', encoding='utf8') as source:
            article = json.load(source, object_hook=CorpusIO.decode_date)
        return article

    @staticmethod
    def encode_date(o):
        if isinstance(o, datetime):
            return DateToStr.date_to_str(o)
    
    @staticmethod
    def decode_date(dct):
        if 'date' in dct:
            dct['date'] = DateToStr.str_to_date(dct['date'])
        return dct


from datetime import datetime

class DateToStr:
    pattern = '%Y-%m-%d_%H:%M:%S'

    @staticmethod
    def date_to_str(date):
        return date.strftime(DateToStr.pattern)
        

    def str_to_date(str_date):
        return datetime.strptime(str_date, DateToStr.pattern)


def encode_date(o):
    if isinstance(o, datetime):
        return DateToStr.date_to_str(o)