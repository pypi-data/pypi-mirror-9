from bambu_oembed.models import Resource
from django.conf import settings
from django.http import HttpResponse
from hashlib import md5
import json

DEBUG = getattr(settings, 'OEMBED_DEBUG', False)
WIDTH = getattr(settings, 'OEMBED_WIDTH', 640)

def resource(request, format):
    endpoint = request.GET.get('endpoint')
    url = request.GET.get('url')
    width = request.GET.get('width') or WIDTH

    if not endpoint or not url:
        return HttpResponse(
            '{"error": "Bad request"}',
            status = 400,
            content_type = 'application/json'
        )

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

            return HttpResponse(
                '{"error": "Invaid oEmbed response"}',
                status = 500,
                content_type = 'application/json'
            )

    data = json.dumps(
        {
            'html': resource.html
        }
    )

    return HttpResponse(
        data,
        content_type = 'application/json'
    )
