import os
import json
from pelican import signals
from indieweb_utils.unfurl import PreviewGenerator


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
    return article.url.rsplit('/', 1)[0]


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
