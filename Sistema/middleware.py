from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [
            reverse('login'),
            reverse('register_user'),
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            if request.path not in self.public_urls:
                return redirect('login')

        response = self.get_response(request)
        return response