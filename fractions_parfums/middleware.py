from django.http import HttpResponseNotFound


class InvalidPathMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        path = request.path.lower()

        # ✅ bloqueia URLs inválidas/maliciosas
        if "http://" in path or "https://" in path:
            return HttpResponseNotFound()

        return self.get_response(request)