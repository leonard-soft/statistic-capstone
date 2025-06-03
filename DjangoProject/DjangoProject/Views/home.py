import django.http.request
from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, Django!", content_type="text/html")
