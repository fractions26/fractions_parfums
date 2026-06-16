from django.http import HttpResponseNotFound


class InvalidPathMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # ✅ LIBERA BOTS IMPORTANTES (WhatsApp / Facebook / Google)
        user_agent = request.META.get("HTTP_USER_AGENT", "").lower()

        allowed_bots = [
            "facebookexternalhit",
            "whatsapp",
            "twitterbot",
            "linkedinbot",
            "googlebot",
        ]

        if any(bot in user_agent for bot in allowed_bots):
            return self.get_response(request)

        # ✅ SEGURANÇA: BLOQUEIA URL MALICIOSA
        path = request.path.lower()

        if "http://" in path or "https://" in path:
            return HttpResponseNotFound()

        # ✅ segue fluxo normal
        return self.get_response(request)