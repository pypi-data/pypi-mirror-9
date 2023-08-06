# -*- coding: utf-8 -*-
from pelican.utils import slugify, truncate_html_words


class Page(object):
    """Represents a page
    Given a content, and metadatas, create an adequate object.

    :param string: the string to parse, containing the original content.
    :param markup: the markup language to use while parsing.
    """
    mandatory_properties = ('title',)

    def __init__(self, content, metadatas={}, settings={}, filename=None):
        self._content = content
        self.translations = []

        self.status = "published"  # default value
        for key, value in metadatas.items():
            setattr(self, key.lower(), value)

        if not hasattr(self, 'author'):
            if 'AUTHOR' in settings:
                self.author = settings['AUTHOR']

        default_lang = settings.get('DEFAULT_LANG').lower()
        if not hasattr(self, 'lang'):
            self.lang = default_lang

        self.in_default_lang = (self.lang == default_lang)

        if not hasattr(self, 'slug'):
            self.slug = slugify(self.title)

        if not hasattr(self, 'save_as'):
            if self.in_default_lang:
                self.save_as = '%s.html' % self.slug
                clean_url = '%s/' % self.slug
            else:
                self.save_as = '%s-%s.html' % (self.slug, self.lang)
                clean_url = '%s-%s/' % (self.slug, self.lang)

        if settings.get('CLEAN_URLS', False):
            self.url = clean_url
        else:
            self.url = self.save_as

        if filename:
            self.filename = filename

        if not hasattr(self, 'date_format'):
            if self.lang in settings['DATE_FORMATS']:
                self.date_format = settings['DATE_FORMATS'][self.lang]
            else:
                self.date_format = settings['DEFAULT_DATE_FORMAT']

        if hasattr(self, 'date'):
            self.locale_date = self.date.strftime(self.date_format.encode('ascii','xmlcharrefreplace')).decode('utf')

        if not hasattr(self, 'summary'):
            self.summary = property(lambda self: truncate_html_words(self.content, 50))

        # store the settings ref.
        self._settings = settings

    def check_properties(self):
        """test that each mandatory property is set."""
        for prop in self.mandatory_properties:
            if not hasattr(self, prop):
                raise NameError(prop)

    @property
    def content(self):
        if hasattr(self, "_get_content"):
            content = self._get_content()
        else:
            content = self._content
        return content


class Article(Page):
    mandatory_properties = ('title', 'date', 'category')


class Quote(Page):
    base_properties = ('author', 'date')


def is_valid_content(content, f):
    try:
        content.check_properties()
        return True
    except NameError as e:
        print u" [info] Skipping %s: impossible to find informations about '%s'" % (f, e)
        return False
