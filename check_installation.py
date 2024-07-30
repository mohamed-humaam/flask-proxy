import importlib.metadata

flask_version = importlib.metadata.version("flask")
requests_version = importlib.metadata.version("requests")

print("Flask version:", flask_version)
print("Requests version:", requests_version)
