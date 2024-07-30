import requests
import json

PROXY_URL = "http://localhost:5001"  # Your proxy server address
HEADERS = {'Content-Type': 'application/json'}

def test_request(method, path, data=None):
    url = f"{PROXY_URL}/{path}"
    response = requests.request(method, url, headers=HEADERS, json=data)
    print(f"{method} Response:", response.status_code)
    print("Headers:", response.headers)
    print("Body:", response.json())
    print("---")

def run_tests():
    # Test GET request
    test_request('GET', 'test')

    # Test POST request
    test_request('POST', 'test', data={"key": "value"})

    # Test PUT request
    test_request('PUT', 'test', data={"key": "updated_value"})

    # Test DELETE request
    test_request('DELETE', 'test')

    # Test error scenario
    test_request('GET', 'error')

if __name__ == "__main__":
    run_tests()