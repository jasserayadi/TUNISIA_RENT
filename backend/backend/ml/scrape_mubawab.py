import os
import requests

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
if not APIFY_TOKEN:
    raise RuntimeError("APIFY_TOKEN environment variable is not set")