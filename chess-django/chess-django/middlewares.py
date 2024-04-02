from django.core.cache import cache
from django.http import HttpResponseForbidden
import os
from dotenv import load_dotenv

load_dotenv()

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user IP is blocked
        ip_address = request.META.get("REMOTE_ADDR")
        if cache.get(f"blocked_{ip_address}"):
            return HttpResponseForbidden(
                f"You are temporarily blocked. If you believe this is an error email: {os.getenv("ADMIN_EMAIL")} - Thanks!"
            )

        response = self.get_response(request)

        # If request was blocked, add to cache
        if response.status_code == 429:  # HTTP 429 Too Many Requests
            cache.set(
                f"blocked_{ip_address}", True, timeout=600
            )  # Timeout is in minutes.

        return response
