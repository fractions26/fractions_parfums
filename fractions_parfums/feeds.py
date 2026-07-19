from django.http import HttpResponse


def google_shopping_feed(request):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
xmlns:g="http://base.google.com/ns/1.0">
<channel>
<title>Fractions Parfums</title>
<link>https://fractionsparfums.com.br</link>
<description>Feed Google Shopping</description>
</channel>
</rss>
"""

    return HttpResponse(
        xml,
        content_type="application/xml"
    )