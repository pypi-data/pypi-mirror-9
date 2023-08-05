from __future__ import unicode_literals
import os
import shutil
import subprocess

from distutils import dir_util
from docutils.core import publish_parts as docutils_publish
from os import environ
from mako import exceptions as mako_exceptions
from mako import lookup as mako_lookup

from . import index
lmap = lambda fn, *it: list(map(fn, *it))  # But Guido, I _like_ `map`!


class Build(object):

    def __init__(self, config):
        'Create config, build blog tree'
        self.config = config
        package_templates = os.path.join(environ.get('VIRTUAL_ENV'),
                                         'bade/templates')
        template_dirs = lmap(os.path.abspath, config.template_dirs)
        self.template_lookup = mako_lookup.TemplateLookup(
            directories=template_dirs + [package_templates]
        )
        self.index = index.BadeIndex(config)

    def clean(self):
        'Carelessly wipe out the build dir'
        shutil.rmtree(self.config.build, ignore_errors=True)

    def render_err(self, name, context):
        'Render a template, with some debugging'
        template = self.template_lookup.get_template(name)
        try:
            return template.render(**context), None
        except:
            if self.config.debug:
                error_html = (mako_exceptions.html_error_template()
                                             .render(full=False)
                                             .decode('utf-8'))
                return error_html, True
            raise

    def write_html(self, template, context, buildpath):
        html, err = self.render_err(template, context)
        htmldir = os.path.dirname(buildpath)
        if not os.path.exists(htmldir) and htmldir:
            os.makedirs(htmldir)
        with open(buildpath, 'w') as htmlfile:
            htmlfile.write(html)
        if err:
            print("Debug HTML written to: {0}".format(buildpath))
        else:
            print("Writing to: {0}".format(buildpath))

    def commit_github(self, rst_path):
        'Return the lastest commit and GitHub link for a given path'
        G = ['git', 'log', '-n', '1', '--pretty=format:%h', '--', rst_path]
        try:
            commit = subprocess.check_output(G).decode('utf-8')
        except subprocess.CalledProcessError:
            commit = 'HEAD'
        return commit

    def page(self, page_path):
        'Build a page'
        context, buildpath = self.index.page_context(page_path)
        self.write_html('page.html', context, buildpath)

    def pages(self):
        lmap(self.page, self.index.pages)

    def post(self, rst_path):
        'Build a page'
        render_context, buildpath = self.index.post_context(rst_path)
        render_context['commit'] = self.commit_github(rst_path)
        self.write_html('post.html', render_context, buildpath)

    def blog_page(self):
        blogtree_rst = self.config.blogtree_rst
        buildpath = (os.path.join(self.config.build, blogtree_rst)
                            .replace('rst', 'html'))
        index_rst, err = self.render_err(blogtree_rst,
                                         self.index.fresh_context())
        if err:
            with open(buildpath, 'w') as htmlfile:
                htmlfile.write(index_rst)
            return
        context = self.index.fresh_context()
        context.update({
            'title_text': self.config.blogtitle,
            'docutils': docutils_publish(index_rst, writer_name='html'),
        })
        return self.write_html('page.html', context, buildpath)

    def index_html(self):
        'Build the site index'
        index_template = self.config.index_template
        render_context = self.index.fresh_context()
        render_context.update({
            'title': 'Home',
        })
        self.write_html(index_template, render_context,
                        os.path.join(self.config.build, 'index.html'))

    def posts(self):
        lmap(self.post, self.index.posts)

    def copy_assetpaths(self):
        'Copy everything specified in the config to the build directory'
        for source in self.config.assetpaths:
            destination = os.path.join(self.config.build, source)
            print("Copying {0} to {1}".format(source, destination))
            if os.path.isdir(source):
                dir_util.copy_tree(source, destination)
            if os.path.isfile(source):
                if os.path.exists(destination):
                    os.remove(destination)
                else:
                    try:
                        os.makedirs(os.path.split(destination)[0])
                    except FileExistsError:
                        pass
                shutil.copy(source, destination)

    def sass(self):
        try:
            sources = self.config.sassin,
            destination = os.path.join(self.config.build, self.config.sassout)
        except AttributeError as exc:
            if 'not configured' in str(exc):
                return
        try:
            import sass_cli  # NOQA
        except ImportError:
            message = 'Sass input configured, but `sass_cli` not installed'
            raise ImportError(message)
        for source in sources:
            subprocess.check_call(['sass', source, destination])

    def run(self):
        'Call all the methods to render all the things'
        if self.config.debug:
            pass
        self.copy_assetpaths()
        self.sass()
        self.pages()
        self.posts()
        self.blog_page()
        self.index_html()
