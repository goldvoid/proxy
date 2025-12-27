import requests
from flask import Flask, request


app = Flask(__name__)


@app.before_request
def before_request():
    response = requests.request(
        url="http://216.9.225.189:9999" + request.path,
        method=request.method,
        data=request.get_data(),
        headers=request.headers
    )
    print(f'Forwarded {request.method} {request.path} - Response: {response.status_code}')
    print(f'response content: {response.content}')
    print(f'response headers: {response.headers}')
    print(f'request path: {request.path}')
    print(f'request method: {request.method}')
    return response.content, response.status_code, {"Content-Type": response.headers.get("Content-Type")}


if __name__ == "__main__":
    app.run()