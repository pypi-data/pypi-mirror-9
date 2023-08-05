import hashlib
import os
import subprocess

from . import utils


class BadeIndex(object):

    def __init__(self, config):
        self.config = config
        self.pages, self.nav = self._page_indexes()
        self.posts_list = self._posts_list()
        self.posts = self._posts_index()
        self.blogtree = self._blogtree()

    def _page_indexes(self):
        pages = dict()
        nav = [{'title_text': 'Home', 'path': '/'}]
        found_blog = False
        for page in self.config.pages:
            if isinstance(page, str):
                docutils = utils.render_rst(page + '.rst')
                page_meta = {
                    'docutils': docutils,
                    'path': self.page_path(page),
                }
                page_meta['title_text'] = utils.strip_tags(docutils['title'])
                nav.append(page_meta)
                page_meta.update({
                    'build': self.page_build(page),
                })
                pages[page] = page_meta
            elif isinstance(page, dict):
                title, path = page.popitem()
                nav.append({'title_text': title, 'path': path})
                if title.lower() == 'blog':
                    found_blog = True
        if found_blog is not True:
            nav.append({'title_text': 'Blog', 'path': '/blog.html'})
        return pages, nav

    def _posts_list(self):
        find = ['find', self.config.blogroot, '-name', '*.rst']
        try:
            paths_list = (subprocess.check_output(find,
                                                  stderr=subprocess.STDOUT)
                                    .decode('utf-8')
                                    .split())
            paths_list.sort(reverse=True)
        except subprocess.CalledProcessError:
            paths_list = list()
        return paths_list

    def _posts_index(self):
        return_dict = dict()
        for rst_path in self.posts_list:
            docutils = utils.render_rst(rst_path)
            return_dict[rst_path] = {
                'id': hashlib.sha1(rst_path.encode('utf-8')).hexdigest(),
                'docutils': docutils,
                'date': utils.post_date(rst_path),
                'build': self.post_build(rst_path),
                'path': self.post_path(rst_path),
            }
            return_dict[rst_path]['title_text'] = utils.strip_tags(docutils['title'])
        for idx, rst_path in enumerate(self.posts_list):
            if idx == 0:
                return_dict[rst_path]['next_post'] = None
            else:
                prev_rst = self.posts_list[idx - 1]
                return_dict[rst_path]['next_post'] = {
                    'title': return_dict[prev_rst]['docutils']['title'],
                    'path': return_dict[prev_rst]['path'],
                }
            if idx == (len(self.posts_list) - 1):
                return_dict[rst_path]['prev_post'] = None
            else:
                next_rst = self.posts_list[idx + 1]
                return_dict[rst_path]['prev_post'] = {
                    'title': return_dict[next_rst]['docutils']['title'],
                    'path': return_dict[next_rst]['path'],
                }
        return return_dict

    def _blogtree(self):
        'Monthly dict of posts'
        D = utils.OrderedDefaultdict
        blogtree = D(lambda: D(list))
        for post_rst in self.posts_list:
            date = utils.post_date(post_rst)
            blogtree[date.year][date.month].append(self.posts[post_rst])
        return blogtree

    def navigation(self):
        'Return index of all pages and posts'
        return {'blogtree': self.blogtree, 'pages': self.pages}

    def page_build(self, rst_path):
        'Return the page to write a rendered post'
        _, page_name = os.path.split(rst_path)
        return os.path.join(self.config.build, page_name + '.html')

    def page_path(self, rst_path):
        'Return the path for href to page'
        return self.page_build(rst_path).replace(self.config.build, '')

    def post_build(self, rst_path):
        'Return the path to write a rendered post'
        return (rst_path[:-4] + '.html').replace(self.config.blogroot,
                                                 self.config.build)

    def post_path(self, rst_path):
        'Return the path for href to post'
        return self.post_build(rst_path).replace(self.config.build, '')

    def fresh_context(self):
        'Return a fresh context with references to nav, blogtree'
        return {
            'nav': self.nav,
            'blogtree': self.blogtree,
        }

    def page_context(self, rst_path):
        'Template context for a page'
        context = self.fresh_context()
        context.update(self.pages[rst_path])
        return context, self.page_build(rst_path)

    def post_context(self, rst_path):
        'Template context for a post'
        context = self.fresh_context()
        context.update(self.posts[rst_path])
        return context, self.post_build(rst_path)
