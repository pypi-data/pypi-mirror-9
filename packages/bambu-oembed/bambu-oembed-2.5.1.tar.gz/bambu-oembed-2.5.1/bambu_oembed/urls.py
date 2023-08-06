from django.conf.urls import patterns, url

urlpatterns = patterns('bambu_oembed.views',
    url(r'^resource\.(?P<format>[\w]+)$', 'resource', name = 'oembed_resource')
)
