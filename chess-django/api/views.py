from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import render
from django_ratelimit.decorators import ratelimit

@ratelimit(key="ip", rate="3/s", block=True)
@require_http_methods(["POST", "GET"])
def vitals(request):
    if request.method == "GET":
        return HttpResponse(":)", content_type="text/plain")
    elif request.method == "POST":
        return JsonResponse({"message": "Kicking!"})


@ratelimit(key="ip", rate="3/s", block=True)
@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


@ratelimit(key="ip", rate="3/s", block=True)
@ensure_csrf_cookie
def set_csrf_token(request):
    return render(request, "api/set_csrf_token.html")
