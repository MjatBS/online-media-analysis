import datetime
import nltk
import re


LANGUAGE = 'russian'


def clear_article(article):
    article = {**article}
    article['title'] = clear_sentence(article["title"])
    article['description'] = clear_text(article['description'])
    article['text'] = clear_text(article['text'])
    return article


def delete_non_alpha_numeric_tokens(tokens):
    words_or_digits = re.compile("[\w\d]+")
    return list(filter(words_or_digits.match, tokens))


def delete_stop_words(tokens):
    raise NotImplementedError()


def lemmatization(tokens):
    raise NotImplementedError()


def clear_text(text) -> list[list]:
    return [clear_sentence(sentence) for sentence in nltk.sent_tokenize(text, language=LANGUAGE)]


def clear_sentence(sentence) -> list:
    sentence = sentence.lower() # needed only for start of sentences. Not for celebrities countries and so on
    tokens = nltk.word_tokenize(sentence, language=LANGUAGE)
    tokens = delete_non_alpha_numeric_tokens(tokens)
    return tokens
