from django import template
from mediagenie.env import get_env
from mediagenie.bundle import html_tag_for_file

register = template.Library()


class MediaNode(template.Node):
    def __init__(self, bundle_name):
        env = get_env()
        self._bundle = env.bundles_by_name[bundle_name]
    def render(self, context):
        return self._bundle.render()


@register.tag
def include_media(parser, token):
    contents = token.split_contents()
    bundle_name = contents[1]
    return MediaNode(bundle_name)


@register.simple_tag
def media_url(url):
    env = get_env()
    if env.production_mode:
        return env.production_base_url + url
    else:
        return env.dev_server_base_url + url
