import os
import json
import opengraph
from micawber.providers import bootstrap_noembed
from pelican import signals


class PreviewGenerator(object):
    def __init__(self):
        self.providers = None

    def initialize(self):
        self.providers = []
        self.providers.append(bootstrap_noembed())

    def preview(self, url):
        if not self.providers:
            self.initialize()
        for p in self.providers:
            result = p.extract(url)
            if result[1]:
                items = result[1].items()
                return list(items)[0][1]

        result = opengraph.OpenGraph(url=url)
        if result:
            return result
        return None


pg = PreviewGenerator()


def setup_previews(generator, metadata):
    metadata['preview'] = None


def attach_preview(generator):
    pfolder = generator.settings.get('PREVIEW_FOLDER', 'previews')
    cache_previews = generator.settings.get('PREVIEW_CACHE', True)
    for article in generator.articles:
        preview_folder = os.path.join(pfolder, get_folder(article))
        preview_file = os.path.join(preview_folder, article.slug)
        if not os.path.isfile(preview_file):
            article.preview = generate_preview(article)
            if cache_previews and article.preview:
                os.makedirs(preview_folder, exist_ok=True)
                save_file(preview_file, article.preview)
        else:
            article.preview = load_file(preview_file)


def generate_preview(article):
    preview_url = get_preview_url(article)
    if preview_url:
        return pg.preview(preview_url)
    else:
        return None


def get_preview_url(article):
    if article.like_of:
        return article.like_of[0]

    if article.in_reply_to:
        return article.in_reply_to[0]

    if article.repost_of:
        return article.repost_of[0]

    if hasattr(article, 'links') and article.links:
        return article.links[0]

    return None


def get_folder(article):
    url = article.url
    return url.rsplit(url, 1)[1]


def load_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_file(filename, contents):
    with open(filename, 'w') as f:
        json.dump(contents, f)


def register():
    signals.article_generator_context.connect(setup_previews)
    signals.article_generator_finalized.connect(attach_preview)
