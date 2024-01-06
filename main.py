import re

import requests
from flask import Flask, request, Response

from constants import *

app = Flask('ivelum')

compiled_re = re.compile(
    r'(?:(?<=\s\")|(?<!=\")(?<![=#<\\/]))'  # lookbehind
    r'(\b(\w{6})\b)' # word len == 6
    r'(?:(?=[\s<]|\"\s)|(?=[!.?,:]\s)(?!:\s?\d)(?![>=/]))',  # lookahead
    flags=re.I
)


@app.route('/', methods=['GET'])
@app.route('/<path>', methods=['GET'])
def main(path=None):
    """
    Proxy all requests to base_url from constants
    and add ™ symbol to words with length == 6
    """
    response = requests.get(
        f'{base_url}{request.path}?{request.query_string.decode("utf-8")}'
    )
    response_content = response.content
    if not response.ok:
        response.headers.pop('Transfer-Encoding')
        response.headers.pop('Content-Encoding')
        return response_content, response.status_code, dict(response.headers)
    mimetypes = ''.join([mt for mt, _ in request.accept_mimetypes])
    if '.js' in request.path:
        return Response(response_content, mimetype='text/javascript')
    elif '.css' in request.path:
        return Response(response_content, mimetype='text/css')
    elif 'text' not in mimetypes:
        if '.svg' in request.path:
            return Response(response_content, mimetype='image/svg+xml')
        elif 'image' in mimetypes:
            return Response(response_content, mimetype='image/*')

    response_content = response_content.decode('utf-8')
    response_content = response_content.replace(
        base_url, f'http://{app_host}:{app_port}'
    )
    # replace html symbols
    for key, value in html_symbols.items():
        response_content = response_content.replace(key, value)
    # add ™ symbol
    response_content = compiled_re.sub(r'\1™', response_content)
    return bytes(response_content, 'utf-8')


if __name__ == '__main__':
    app.run(host=app_host, port=app_port)
