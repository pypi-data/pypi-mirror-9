import collections
import datetime
import os
from docutils.core import publish_parts as docutils_publish
from html.parser import HTMLParser

class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        if not self.fed:
            return self.rawdata
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class OrderedDefaultdict(collections.OrderedDict):

    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default


def render_rst(rst_path):
    with open(rst_path, 'r') as rst_file:
        rst_string = rst_file.read()
    return docutils_publish(rst_string, writer_name='html')


def rst_title(rst_path):
    'Get the title of a page from the path'
    bare_path, ext = os.path.splitext(rst_path)
    slug = os.path.split(bare_path)[-1]
    return ' '.join(slug.split('-')).capitalize()


def post_date(rst_path):
    'datetime from post path'
    return datetime.date(*map(int, rst_path.split(os.sep)[1:4]))
