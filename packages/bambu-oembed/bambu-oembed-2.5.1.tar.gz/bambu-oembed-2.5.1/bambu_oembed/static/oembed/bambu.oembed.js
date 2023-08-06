jQuery(document).ready(
    function($) {
        $('.bambu-oembed-resource').each(
            function() {
                var resource = $(this);
                var endpoint = resource.data('endpoint');
                var url = resource.data('url');
                var format = resource.data('format');
                var width = resource.outerWidth(true);
                var waypoint = new Waypoint(
                    {
                        element: resource.get(0),
                        handler: function(direction) {
                            if(resource.data('bambu.oembed.bound')) {
                                return;
                            }

                            resource.find('.progress').addClass('active');
                            setTimeout(
                                function() {
                                    $.ajax(
                                        {
                                            url: '/oembed/resource.' + format,
                                            dataType: 'json',
                                            data: [
                                                'endpoint=' + escape(endpoint),
                                                'url=' + escape(url),
                                                'width=' + width
                                            ].join('&'),
                                            context: resource,
                                            success: function(data) {
                                                if(data.html) {
                                                    $(this).html(data.html).removeAttr(
                                                        'data-endpoint'
                                                    ).removeAttr(
                                                        'data-url'
                                                    ).removeAttr(
                                                        'data-width'
                                                    ).removeAttr(
                                                        'data-format'
                                                    ).addClass('loaded');
                                                }
                                            },
                                            error: function(data) {
                                                resource.html(
                                                    '<div class="alert alert-danger"><p>This resource couldn&rsquo;t be embedded.</p></div>'
                                                ).addClass('error');
                                            }
                                        }
                                    );
                                },
                                100
                            )

                            resource.data('bambu.oembed.bound', true);
                        },
                        offset: '100%'
                    }
                );

                resource.html(
                    '<div class="progress progress-striped"><div class="progress-bar progress-bar-info" style="width: 100%;"></div></div>'
                );
            }
        )
    }
)
