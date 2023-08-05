from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import grequests

@csrf_exempt
def listener(request):
    return repeat(request)

def repeat(request, addresses=("http://127.0.0.3:8000", "http://127.0.0.2:8000")):
    if request.method == 'POST':
        # CREATE HEADERS
        headers = {'content-type': request.META['CONTENT_TYPE']}

        # REPEAT POST
        for address in addresses:
            r = grequests.post(address,data=request.body, headers=headers)
        
        return HttpResponse(request.body, content_type=request.META['CONTENT_TYPE'])
    print "GET"
    return HttpResponse("")