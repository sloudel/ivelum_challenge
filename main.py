import re

import requests
from flask import Flask, request, Response

base_url = 'https://news.ycombinator.com'
app_host = '127.0.0.1'
app_port = 5000

app = Flask('ivelum')


@app.route('/', methods=['GET'])
@app.route('/<path>', methods=['GET'])
def main(path=None):
    """
    Proxy all requests to Hacker News portal
    and add ™ to words with length == 6
    """
    response = requests.get(
        f'{base_url}{request.path}'
        f'?{request.query_string.decode("utf-8")}'
    )
    response_content = response.content
    if not response.ok:
        return response_content, response.status_code, dict(response.headers)
    mimetypes = ''.join([mt for mt, _ in request.accept_mimetypes])
    if '.css' in request.path:
        return Response(response_content, mimetype='text/css')
    elif 'text' not in mimetypes:
        if '.svg' in request.path:
            return Response(response_content, mimetype='image/svg+xml')
        elif 'image' in mimetypes:
            return Response(response_content, mimetype='image/*')


    response_content = response_content.decode('utf-8')
    # replace hacker news portal urls with proxy url
    response_content = response_content.replace(
        base_url, f'http://{app_host}:{app_port}'
    )
    # replace one len(word) == 6 in a tag
    response_content = re.sub(
        r'>(\b(\w{6})\b)<', r'>\1™<',
        response_content, flags=re.I
    )
    # replace len(word) == 6 and symbol after it
    for symbol in ['.', '?']:
        response_content = re.sub(
            r'(\b(\w{6})\b)' + "\\" + symbol, r'\1™' + symbol,
            response_content, flags=re.I
        )
    for symbol in [',', ' ', '!']:
        response_content = re.sub(
            r'(\b(\w{6})\b)' + symbol, r'\1™' + symbol,
            response_content, flags=re.I
        )
    return bytes(response_content, 'utf-8')


if __name__ == '__main__':
    app.run(host=app_host, port=app_port)
