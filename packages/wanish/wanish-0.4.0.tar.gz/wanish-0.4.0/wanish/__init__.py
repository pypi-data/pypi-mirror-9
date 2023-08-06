from lxml import etree
import requests
from requests.exceptions import ConnectionError, Timeout
from lxml.html import document_fromstring

from wanish.cleaner import html_cleaner, ArticleExtractor
from wanish.encoding import get_encoding
from wanish.images import get_image_url
from wanish.title import shorten_title


# Initialization of lang analyzer. Takes some time.
from wanish.langid import LanguageIdentifier, model
lang_identifier = LanguageIdentifier.from_modelstring(model)

from wanish.summarizer import get_plain_text


# Template of the resulting article
ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="%(language)s">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wanish cleaner</title>
    %(description_node)s
</head>
<body>

<article itemscope itemtype="http://schema.org/Article">
    <meta itemprop="inLanguage" content="%(language)s">
    %(image_url_node)s
    <h1 itemprop="headline">%(title)s</h1>
    <div itemprop="articleBody">
        %(image_url_img)s
        %(clean_html)s
    </div>
</article>

</body>
</html>"""


class Wanish():

    def __init__(self, url=None, positive_keywords=None, negative_keywords=None, summary_sentences_qty=5, headers=None):
        """
        Initialization of the class. If url is set, it gets performed.

        :param url: web-page url of the document
        :param positive_keywords: list of keywords, which are likely to be seen in classes or ids of tags
        :param negative_keywords: list of keywords, which are unlikely to be seen in classes or ids of tags
        :param summary_sentences_qty: maximum quantity of summary sentences
        :param headers: custom headers for GET request to obtain web page of the article
        """
        self._article_extractor = ArticleExtractor(positive_keywords=positive_keywords,
                                                   negative_keywords=negative_keywords)

        self.url = None  # source web-page url

        self.title = None  # document's title
        self.image_url = None  # document's image url
        self.language = None  # document's article language
        self.clean_html = None  # cleaned html of the article
        self.description = None  # summarized description (text only)

        self.error_msg = None  # error message

        self._source_html = None  # source html of the document (lxml doc)
        self._charset = None  # source html encoding
        self._headers = headers if type(headers) == dict else {}  # custom headers for GET request

        # summarized text sentences quantity
        try:
            self._summary_sentences_qty = summary_sentences_qty
        except (TypeError, ValueError):
            self._summary_sentences_qty = 5

        # perform the url if defined
        if url:
            self.perform_url(url)

    def perform_url(self, url):
        """
        Perform an article document by designated url

        :param url: web-page url of the document
        """
        self.url = url
        self.title = self.image_url = self.language = self.description = \
            self.clean_html = self.error_msg = self._charset = None

        if not self.url:
            self.error_msg = 'Empty or null URL to perform'
            return

        # get the page (bytecode)
        try:
            web_page = requests.get(self.url, headers=self._headers)
            self.url = web_page.url

            raw_html = web_page.content

            self._charset = get_encoding(raw_html)
            raw_html_str = raw_html.decode(self._charset)

            # getting and cleaning the document
            self._source_html = document_fromstring(raw_html_str)
            self._source_html = html_cleaner.clean_html(self._source_html)

            # making links absolute
            self._source_html.make_links_absolute(self.url, resolve_base_href=True)

        except ConnectionError as e:
            self.error_msg = e
        except Timeout as e:
            self.error_msg = e
        except TypeError as e:
            self.error_msg = e
        finally:
            if self.error_msg:
                return

        if self._source_html is not None:

            # obtaining title
            self.title = shorten_title(self._source_html)

            # obtaining image url
            self.image_url = get_image_url(self._source_html)
            if self.image_url is not None:
                image_url_node = "<meta itemprop=\"image\" content=\"%s\">" % self.image_url
                image_url_img = "<img src=\"%s\" />" % self.image_url
            else:
                image_url_node = image_url_img = ""

            # clean html
            self.clean_html = self._article_extractor.get_clean_html(source_html=self._source_html)

            # summarized description, requires clean_html
            if self.clean_html:
                self.description, self.language = get_plain_text(etree.XML(self.clean_html),
                                                                 self._summary_sentences_qty)
                description_node = "<meta name=\"description\" content=\"%s\">" if self.description else ""

                # filling the template
                self.clean_html = ARTICLE_TEMPLATE % {
                    'language': self.language,
                    'title': self.title,
                    'image_url_node': image_url_node,
                    'image_url_img': image_url_img,
                    'description_node': description_node,
                    'clean_html': self.clean_html
                }