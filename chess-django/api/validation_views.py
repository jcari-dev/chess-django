from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import chess
from .utils import parse_board

@require_http_methods(["POST"])
def validate_move(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        parse_board({"board": data['board']})
        
        print(data)
        
        print("---------")
        
        return JsonResponse({"valid": True})
