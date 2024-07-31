from flask import Flask, request, jsonify, Response
import requests
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import TimedRotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
DESTINATION_URL = os.environ.get('DESTINATION_URL', 'https://api.cinex.pro/api/payment/checkout')
SECRET_KEY = os.environ.get('SECRET_KEY', 'goruboe')
RATE_LIMIT = os.environ.get('RATE_LIMIT', '10 per minute')

# Set up rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[RATE_LIMIT]
)

def setup_logger():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger('proxy_logger')
    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(log_dir, 'proxy.log')
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
    file_handler.suffix = "%Y-%m-%d.log"

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit(RATE_LIMIT)
def proxy(path):
    logger.info(f"Received request: {request.method} {request.url}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request body: {request.get_data().decode('utf-8')}")

    if SECRET_KEY in request.path:
        logger.info(f"Access granted with secret key: {request.url}")
        return "Access granted to your site through the proxy!"

    try:
        target_url = f"{DESTINATION_URL}/{path}"
        logger.info(f"Forwarding request to: {target_url}")

        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )

        logger.info(f"Received response from {target_url} with status {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response content: {response.text[:200]}...")  # Log first 200 characters

        if response.status_code == 404:
            logger.warning(f"404 Not Found error from destination for path: {path}")
            return jsonify({'error': 'Resource not found on the destination server'}), 404

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(response.content, response.status_code, headers)

    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while requesting {target_url}")
        return jsonify({'error': 'Request to destination timed out'}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error occurred while requesting {target_url}")
        return jsonify({'error': 'Could not connect to destination'}), 502
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while requesting {target_url}: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

if __name__ == '__main__':
    logger.info("Starting proxy server")
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)