from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import render
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from datetime import datetime

@ratelimit(key="ip", rate="5/s", block=True)
@require_http_methods(["POST", "GET"])
def vitals(request):
    cache_test = cache.get('date')
    
    if request.method == "GET":
        if not cache_test:    
    
            cache.set('date', datetime.now(), timeout=3600*24)
            cache_test = cache.get('date')

        return HttpResponse(f":) {cache_test}", content_type="text/plain")
    elif request.method == "POST":
        return JsonResponse({"message": "Kicking!"})


@ratelimit(key="ip", rate="5/s", block=True)
@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


@ratelimit(key="ip", rate="/s", block=True)
@ensure_csrf_cookie
def set_csrf_token(request):
    return render(request, "api/set_csrf_token.html")
