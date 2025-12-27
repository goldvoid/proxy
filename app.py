import requests
from flask import Flask, request
import logging

# Set up proper logging (visible in Vercel logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TARGET_BASE = "http://216.9.225.189:9999"

@app.before_request
def proxy_and_log():
    # Build target URL
    target_url = TARGET_BASE + request.path
    if request.query_string:
        target_url += '?' + request.query_string.decode('utf-8')

    try:
        # Forward the request
        resp = requests.request(
            method=request.method,
            url=target_url,
            data=request.get_data(),
            headers={
                k: v for k, v in request.headers.items()
                if k.lower() not in ('host', 'content-length')  # avoid issues
            },
            allow_redirects=False,
            timeout=25
        )

        # Log important info (this WILL show in Vercel logs)
        logger.info("═" * 70)
        logger.info(f"FORWARDED → {request.method} {request.path}")
        logger.info(f"Target URL: {target_url}")
        logger.info(f"Response Status: {resp.status_code}")
        logger.info(f"Response Headers: {dict(resp.headers)}")

        # Log body only if not too large (Vercel log limit ~4KB/line)
        content_preview = resp.content[:1000].decode('utf-8', errors='ignore')
        logger.info(f"Response Content Preview: {content_preview}...")

        logger.info("═" * 70)

        # Return the real response to the client
        return (
            resp.content,
            resp.status_code,
            {"Content-Type": resp.headers.get("Content-Type", "text/plain")}
        )

    except Exception as e:
        logger.error(f"Proxy error: {str(e)}")
        return f"Proxy error: {str(e)}", 502, {"Content-Type": "text/plain"}


# Vercel requires no app.run() in production
# Keep this only for local testing (comment out on deploy)
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)