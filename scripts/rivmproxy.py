from urllib.parse import urlparse
import os

json_enabled = True
csv_enabled = True

def rivm_url(url):
    prox = os.getenv('RIVM_PROXY')

    if not prox:
        return url

    if not json_enabled and url.lower().strip().endswith('.json'):
        return url

    if not csv_enabled and url.lower().strip().endswith('.csv'):
        return url

    prox_url = urlparse(prox)
    new_url = urlparse(url)

    return new_url._replace(scheme=prox_url.scheme, netloc=prox_url.netloc).geturl()
