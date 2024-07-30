from flask import Flask, request, jsonify, Response
import requests
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.handlers import TimedRotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
DESTINATION_URL = os.environ.get('DESTINATION_URL', 'https://example.com/api')
SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
RATE_LIMIT = os.environ.get('RATE_LIMIT', '10 per minute')

# Set up rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[RATE_LIMIT]
)
limiter.logger = logger


def setup_logger():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger('proxy_logger')
    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(log_dir, 'proxy.log')
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    file_handler.suffix = "%Y-%m-%d.log"

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()

@app.route('/receive', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit(RATE_LIMIT)
def proxy():
    logger.info(f"Received {request.method} request")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Request body: {request.get_data().decode('utf-8')}")
    
    try:
        response = requests.request(
            method=request.method,
            url=DESTINATION_URL,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )
        
        logger.info(f"Forwarded {request.method} request to {DESTINATION_URL}")
        logger.info(f"Received response from {DESTINATION_URL} with status {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response body: {response.text}")
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(response.content, response.status_code, headers)
    
    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while requesting {DESTINATION_URL}")
        return jsonify({'error': 'Request to destination timed out'}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error occurred while requesting {DESTINATION_URL}")
        return jsonify({'error': 'Could not connect to destination'}), 502
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while requesting {DESTINATION_URL}: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

if __name__ == '__main__':
    logger.info("Starting proxy server")
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=os.environ.get('DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port)
