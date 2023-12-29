import requests
from flask import Flask, request
from bs4 import BeautifulSoup

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
    print(request.path)
    print(request.query_string)
    response_content = requests.get(
        f'{base_url}{request.path}?{request.query_string.decode("utf-8")}'
    ).content
    try:
        response_content = response_content.decode('utf-8')
        response_content = response_content.replace(
            base_url, f'http://{app_host}:{app_port}'
        )
    except UnicodeDecodeError:
        return bytes(response_content)  # return images, styles etc.
    soup = BeautifulSoup(response_content, 'html.parser')
    comments = soup.find_all(attrs={'class': 'comment'})
    replaced = set()
    for comment in comments or []:
        source_text = comment.get_text()
        for word in source_text.split(' '):
            if len(word) == 6 and word not in replaced:
                replaced.add(word)
                response_content = response_content.replace(word, word + '™')
    return bytes(response_content, 'utf-8')


if __name__ == '__main__':
    app.run(host=app_host, port=app_port)
