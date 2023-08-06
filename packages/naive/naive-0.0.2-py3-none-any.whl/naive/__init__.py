import markdown
import os
import sass
import shutil
import yaml

from datetime import datetime, timedelta, timezone
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.abspath(os.curdir)

with open(os.path.join(BASE_DIR, '_settings.yml'), 'r', encoding='utf-8') as f:
    settings = yaml.load(f.read())


class Page():
    """Article like author info."""

    def __init__(self, markdown_data):
        md = markdown.Markdown(extensions=['markdown.extensions.meta',
                                           'markdown.extensions.footnotes'])
        html = md.convert(markdown_data)
        self.title = md.Meta['title'][0]
        self.date = md.Meta['date'][0]
        self.modified = md.Meta['modified'][0]
        self.slug = md.Meta['slug'][0]
        self.authors = md.Meta['author'][0]
        self.html = html

    def __repr__(self):
        return "<Page:{0}, {1}, {2}>".format(self.title, self.date, self.slug)


class Post():
    """Blog post."""

    def __init__(self, markdown_data):
        md = markdown.Markdown(extensions=['markdown.extensions.meta',
                                           'markdown.extensions.footnotes'])
        html = md.convert(markdown_data)
        date = datetime.strptime(md.Meta['date'][0], '%Y-%m-%d %H:%M')
        tz = timezone(timedelta(hours=settings['TIMEZONE_OFFSET_HOUR']))
        self.title = md.Meta['title'][0]
        self.date = date.replace(tzinfo=tz)
        self.datestr = self.date.strftime('%A, %B %d, %Y')
        self.modified = md.Meta['modified'][0]
        self.category = md.Meta['category'][0]
        self.tags = md.Meta['tags']
        self.slug = md.Meta['slug'][0]
        self.authors = md.Meta['authors'][0]
        self.summary = md.Meta['summary'][0]
        self.html = html
        self.url = "/{0}/{1}/{2}".format(settings['PATHS']['output_post'],
                                         self.date.strftime('%Y/%m/%d'),
                                         self.slug)

    def __repr__(self):
        return "<Post:{0}, {1}, {2}>".format(self.title, self.date, self.slug)


def write_to_path(content, file_path):
    """Write content to file on the path.

    If there are no directories, make directories.
    """
    dirname = os.path.dirname(file_path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def copy(from_file_path, to_file_path):
    """Copy file with creating directories."""
    dirname = os.path.dirname(to_file_path)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    shutil.copy2(from_file_path, to_file_path)


class NaiveSite():
    def __init__(self):
        self.paths = settings['PATHS']
        self.site = settings['SITE']
        self.pages = self._get_pages()
        self.posts = self._get_posts()
        self.templates = self._get_templates()

    def generate(self):
        self._create_page_htmls()
        self._create_post_htmls()
        self._create_index_page()
        self._create_archive_page()
        self._create_atom_feed()
        self._create_404_page()
        self._compile_sass()
        # self._copy_static_folder()
        self._copy_bower_components()

    def _get_pages(self):
        """Read Markdown files from pages folder and return list of Pages."""
        print("Read pages.")
        pages = []
        page_path = os.path.join(BASE_DIR, self.paths['page'])
        for path, subdirs, files in os.walk(page_path):
            for filename in files:
                if os.path.splitext(filename)[1] == '.md':
                    page = os.path.join(path, filename)
                    print(".", end="")
                    with open(page, 'r', encoding='utf-8') as f:
                        pages.append(Page(f.read()))
        print(" {} pages found.\n".format(len(pages)))
        return pages

    def _get_posts(self):
        """Read Markdown files from posts folder and return list of Posts."""
        print("Read posts.")
        posts = []
        post_path = os.path.join(BASE_DIR, self.paths['post'])
        for path, subdirs, files in os.walk(post_path):
            for filename in files:
                if os.path.splitext(filename)[1] == '.md':
                    post = os.path.join(path, filename)
                    print(".", end="")
                    with open(post, 'r', encoding='utf-8') as f:
                        posts.append(Post(f.read()))
        print(" {} posts found.\n".format(len(posts)))
        return posts

    def _get_templates(self):
        """Get templates from template files."""
        template_path = os.path.join(BASE_DIR, self.paths['template'])
        template_env = Environment(loader=FileSystemLoader(template_path))
        templates = {}
        for k, v in settings['TEMPLATES'].items():
            templates[k] = template_env.get_template(v)
        return templates

    def _create_page_htmls(self):
        """Create page htmls and write to output folder."""
        for page in self.pages:
            content = self.templates['page'].render(page=page, site=self.site)
            path = os.path.join(BASE_DIR, self.paths['output'],
                                page.slug, 'index.html')
            write_to_path(content, path)

    def _create_post_htmls(self):
        """Create post htmls and write to output folder."""
        for post in self.posts:
            content = self.templates['post'].render(post=post, site=self.site)
            date_path = post.date.strftime('%Y/%m/%d')
            path = os.path.join(BASE_DIR, self.paths['output'],
                                self.paths['output_post'],
                                date_path, post.slug, 'index.html')
            write_to_path(content, path)

    def _create_index_page(self):
        """Create index page html and write to output folder."""
        posts = sorted(self.posts, key=lambda post: post.date,
                       reverse=True)[:10]
        content = self.templates['index'].render(posts=posts, site=self.site)
        path = os.path.join(BASE_DIR, self.paths['output'], 'index.html')
        write_to_path(content, path)

    def _create_archive_page(self):
        """Create archive page html and write to output folder."""
        posts = sorted(self.posts, key=lambda post: post.date, reverse=True)
        content = self.templates['archive'].render(posts=posts, site=self.site)
        path = os.path.join(BASE_DIR, self.paths['output'],
                            self.paths['output_archive'], 'index.html')
        write_to_path(content, path)

    def _create_atom_feed(self):
        """Create ATOM feed xml and write to output folder."""
        posts = sorted(self.posts, key=lambda post: post.date,
                       reverse=True)[:10]
        content = self.templates['atom'].render(posts=posts, site=self.site)
        path = os.path.join(BASE_DIR, self.paths['output'], 'atom.xml')
        write_to_path(content, path)

    def _create_404_page(self):
        """Create 404 error page html and write to output folder."""
        content = self.templates['error404'].render(site=self.site)
        path = os.path.join(BASE_DIR, self.paths['output'], '404.html')
        write_to_path(content, path)

    def _compile_sass(self):
        """Search SASS files and compile into CSS."""
        static_path = os.path.join(BASE_DIR, self.paths['static']) + '/css'
        os.chdir(static_path)
        for path, subdirs, files in os.walk(os.curdir):
            for filename in files:
                if os.path.splitext(filename)[-1] == '.scss':
                    sass_path = os.path.join(static_path,
                                             path.replace('./', ''),
                                             filename)
                    css_path = sass_path.replace('.scss', '.css')
                    css = sass.compile(filename=sass_path)
                    write_to_path(css, css_path)
        os.chdir(BASE_DIR)

    def _copy_static_folder(self):
        """Copy static files and folders like CSS, JS, IMG to output folder."""
        static_path = os.path.join(BASE_DIR, self.paths['static'])
        os.chdir(static_path)
        for path, subdirs, files in os.walk(os.curdir):
            output_path = os.path.join(BASE_DIR, self.paths['output'],
                                       path.replace('./', ''))
            for filename in files:
                original_file = os.path.join(path, filename)
                output_file = os.path.join(output_path, filename)
                copy(original_file, output_file)
        os.chdir(BASE_DIR)

    def _copy_bower_components(self):
        """Copy bower component files to output folder."""
        for path in settings['BOWER_COMPONENTS']:
            original = os.path.join(BASE_DIR, self.paths['bower'], path)
            output = os.path.join(BASE_DIR, self.paths['output'],
                                  self.paths['output_bower'], path)
            copy(original, output)


def main():
    NaiveSite().generate()
