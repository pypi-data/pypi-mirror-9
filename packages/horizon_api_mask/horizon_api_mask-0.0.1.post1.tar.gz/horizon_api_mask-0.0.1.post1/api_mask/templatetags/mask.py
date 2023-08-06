import re
import socket
from django import template
from django.conf import settings

register = template.Library()

ip = re.compile("[0-9]+(?:\.[0-9]+){3}")
protocol = re.compile("^http[s]?")

@register.filter
def mask(url):
    if isinstance(url, basestring):
        if getattr(settings, "API_MASK_PROTOCOL", "https") == "https":
            url = protocol.sub("https", url)
        return ip.sub(getattr(settings,"API_MASK_URL", socket.getfqdn()), url)
    return url