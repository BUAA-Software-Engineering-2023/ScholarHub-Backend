import json

from django.http.response import JsonResponse

def search_work_view(request):
    if (request.method != 'GET')
