from django.template import Library
from django.conf import settings
from django.utils.safestring import mark_safe
from bambu_oembed import URL_REGEX, URL_PATTERNS
from bambu_oembed.models import Resource
import re

PATTERNS = list(URL_PATTERNS) + getattr(settings, 'OEMBED_URL_PATTERNS', [])
WIDTH = getattr(settings, 'OEMBED_WIDTH', 640)
DEBUG = getattr(settings, 'OEMBED_DEBUG', False)
AJAX = getattr(settings, 'OEMBED_AJAX', False)

register = Library()

@register.filter()
def oembed(value, width = WIDTH):
    """
    Takes an HTML or Markdown string and replaces oEmbed references (single lines with a URL to a resource
    that supports oEmbed) with the HTML representing the object.

    :param value: The string to replace
    :param width: The maximum width of a resource (typically video or image)
    """

    if not '<p' in value and not '</p>' in value:
        value = '<p>%s</p>' % value

    match = URL_REGEX.search(value)
    if match is None:
        match = URL_REGEX.search(value)

    while not match is None and match.end() <= len(value):
        start = match.start()
        end = match.end()
        groups = match.groups()

        if len(groups) > 0:
            url = groups[0]
            inner = '<p><a href="%(url)s">%(url)s</a></p>' % {
                'url': url
            }

            for (pattern, endpoint, format) in PATTERNS:
                if not re.match(pattern, url, re.IGNORECASE) is None:
                    if AJAX:
                        inner = '<div class="bambu-oembed-resource" data-url="%s" data-endpoint="%s" data-format="%s" data-width="%s"></div>' % (
                            url, endpoint, format, width
                        )
                    else:
                        try:
                            resource = Resource.objects.get(
                                url = url,
                                width = width
                            )
                        except Resource.DoesNotExist:
                            try:
                                resource = Resource.objects.create_resource(
                                    url, width, endpoint, format
                                )
                            except:
                                if DEBUG:
                                    raise

                                break

                        inner = resource.html
                    break
        else:
            inner = ''

        value = value[:start] + inner + value[end:]
        match = URL_REGEX.search(value, start + len(inner))

    return mark_safe(value)
