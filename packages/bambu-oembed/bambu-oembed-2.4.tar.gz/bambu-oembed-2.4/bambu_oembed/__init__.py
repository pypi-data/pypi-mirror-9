from django.conf import settings
import requests

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

import re
__version__ = '2.4'

URL_REGEX = re.compile(
    r'<p>(?P<url>(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+))<\/p>', re.IGNORECASE
)

URL_PATTERNS = (
    (r'^https?://(?:.+\.)?blip\.tv/file/.+$',
        'https://blip.tv/oembed/', 'json'
    ),
    (r'^https?://(?:www\.)?dailymotion\.com/video/.+$',
        'https://www.dailymotion.com/api/oembed/', 'json'
    ),
    (r'^https?://(?:www\.)?dotsub\.com/view/.+$',
        'https://dotsub.com/services/oembed', 'json'
    ),
    (r'^https?://(?:www\.)?flickr\.com/photos/.+$',
        'https://www.flickr.com/services/oembed/', 'xml'
    ),
    (r'^https?://(?:www\.)?nfb\.ca/film/.+$',
        'https://www.nfb.ca/remote/services/oembed/',
        'xml'
    ),
    (r'^https?://(.+\.)?photobucket\.com/(?:albums|groups)/.+$',
        'https://api.photobucket.com/oembed', 'json'
    ),
    (r'^https?://(?:www\.)?revision3\.com/.+$',
        'https://revision3.com/api/oembed/', 'json'
    ),
    (r'^https?://(?:www\.)?scribd\.com/doc/.+$',
        'https://www.scribd.com/services/oembed', 'json'
    ),
    (r'^https?://(?:www\.)?soundcloud\.com/(?:[^/]+)/(?:[^/]+)/?$',
        'https://soundcloud.com/oembed', 'json'
    ),
    (r'^https?://(?:www\.)?twitter\.com/(?:#!/)?[\w]+/status/\d+/?$',
        'https://api.twitter.com/1/statuses/oembed.json', 'json'
    ),
    (r'^https?://(?:www\.)?viddler\.com/v/.+$',
        'https://www.viddler.com/oembed/?format=json', 'json'
    ),
    (r'^https?://(?:www\.)?vimeo\.com/.+$',
        'https://vimeo.com/api/oembed.json', 'json'
    ),
    (r'^https?://(?:www\.)?yfrog\.(?:com|ru|com\.tr|it|fr|co\.il|co\.uk|com\.pl|pl|eu|us)/.+$',
        'https://www.yfrog.com/api/oembed', 'json'
    ),
    (r'^https?://(?:www\.)?youtube\.com/watch\?v=.+$',
        'https://www.youtube.com/oembed', 'json'
    ),
    (r'^https?://(?:www\.)?youtu\.be/.+$',
        'https://www.youtube.com/oembed', 'json'
    )
)

def get_oembed_response(url, endpoint, format, width = None):
    if not width:
        width = getattr(settings, 'OEMBED_WIDTH', 640)

    if format == 'json':
        mimetype = 'application/json'
    elif format == 'xml':
        mimetype = 'text/xml'
    elif format != 'html':
        raise Exception('Handler configured incorrectly (unrecognised format %s)' % format)

    params = {
        'url': url,
        'scheme': 'https'
    }

    if int(width) > 0:
        params['width'] = width
        params['maxwidth'] = width

    if not callable(endpoint):
        return requests.get(
            endpoint,
            params = params,
            headers = {
                'Accept': mimetype,
                'User-Agent': 'bambu-tools/2.3.1'
            }
        )
    else:
        return endpoint(url)

def get_oembed_content(url, endpoint, format, width = None):
    response = get_oembed_response(url, endpoint, format, width)

    if format == 'json':
        json = response.json()

        if 'html' in json:
            return json.get('html')
        elif 'thumbnail_url' in json:
            return '<a href="%(resource)s"><img alt=="%(title)s" src="%(url)s" /></a>' % {
                'title': json['title'],
                'url': json['thumbnail_url'],
                'resource': url,
            }
        else:
            raise Exception('Response not understood', json)
    else:
        try:
            xml = ElementTree.parse(response)
        except:
            raise Exception('Not an XML response')

        try:
            return xml.getroot().find('html').text or ''
        except:
            if not xml.find('url') is None:
                return '<a href="%(resource)s"><img alt=="%(title)s" src="%(url)s" /></a>' % {
                    'title': xml.find('title') and xml.find('title').text or '',
                    'url': xml.find('url').text,
                    'resource': url
                }
            else:
                raise Exception('No embeddable content found')
