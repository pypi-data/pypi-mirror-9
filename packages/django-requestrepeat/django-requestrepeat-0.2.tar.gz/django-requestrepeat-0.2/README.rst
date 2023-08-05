=====
requestrepeat
=====

A Django app that will receive a web POST request and 
resend that same POST to several servers.

Quick start
-----------

1. Add "requestrepeat" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'requestrepeat',
    )

2. Add some code

Usage:
    repeat(request,addresses=("http://my.first.url.com/ipn", "http://my.second.url.com/ipn/"))

Example:

    urls.py
    url("^repeater/$", 'requestrepeat.views.listener', name='listener'),

    views.py
    
    @csrf_exempt
    def listener(request):
        return repeat(request,addresses=("http://127.0.0.4:8000", "http://127.0.0.6:8000"))

5. Send a POST request with data to http://127.0.0.1:8000/repeater/ replicate that post to several urls.