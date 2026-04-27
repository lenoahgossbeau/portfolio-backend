from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def subscriptions_view(request):
    if request.method == 'GET':
        subscriptions = [
            {
                "id": 1,
                "profile_id": "PROF-001",
                "start_date": "2025-01-01",
                "end_date": "2026-01-01",
                "type": "Premium",
                "payment_method": "Carte bancaire",
                "amount": 29.99
            },
            {
                "id": 2,
                "profile_id": "PROF-002",
                "start_date": "2025-02-15",
                "end_date": "2026-02-15",
                "type": "Standard",
                "payment_method": "PayPal",
                "amount": 19.99
            }
        ]
        return JsonResponse(subscriptions, safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscriptions/', subscriptions_view, name='subscriptions'),
]