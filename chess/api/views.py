from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def vitals(request):
    return JsonResponse({"message": "Listening"})
