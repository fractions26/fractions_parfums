from apps.logs.models import AcessoPagina


class AcessoPaginaMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        try:

            caminho = request.path

            ip = request.META.get(
                'HTTP_X_FORWARDED_FOR',
                request.META.get('REMOTE_ADDR', '')
            )

            if ',' in ip:
                ip = ip.split(',')[0].strip()

            # HOME
            if caminho == '/':

                AcessoPagina.objects.create(
                    tipo='HOME',
                    url=caminho,
                    ip=ip
                )

            # PRODUTO
            elif '/produto/' in caminho:

                AcessoPagina.objects.create(
                    tipo='PRODUTO',
                    url=caminho,
                    ip=ip
                )

            # PEDIDO FINALIZADO
            elif (
                '/pedido/' in caminho
                and 'sucesso' in caminho
            ):

                AcessoPagina.objects.create(
                    tipo='PEDIDO',
                    url=caminho,
                    ip=ip
                )

        except Exception:
            pass

        return response