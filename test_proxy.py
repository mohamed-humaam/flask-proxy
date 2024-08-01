import requests
import json

PROXY_URL = "https://830c89d2-1d8c-4d08-ab5e-ce886d3bd24f.cinex.pro"  # Your proxy server address
HEADERS = {'Content-Type': 'application/json'}

def test_request(method, path, data=None):
    url = f"{PROXY_URL}/{path}"
    response = requests.request(method, url, headers=HEADERS, json=data)
    print(f"{method} {path} Response:", response.status_code)
    print("Headers:", response.headers)
    print("Body:", response.text)
    print("---")

def run_tests():
    # Test GET request
    test_request('GET', 'api/payment/checkout')

    # Test POST request
    test_request('POST', 'api/payment/checkout', data={"amount": 100, "currency": "USD"})

    # Test PUT request
    test_request('PUT', 'api/payment/checkout', data={"id": 1, "status": "completed"})

    # Test DELETE request
    test_request('DELETE', 'api/payment/checkout')

    # Test secret key access
    test_request('GET', 'goruboe')

    # Test non-existent path
    test_request('GET', 'non_existent_path')

if __name__ == "__main__":
    run_tests()