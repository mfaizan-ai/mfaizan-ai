from fastapi import FastAPI, Request
from fastapi.responses import Response
from datetime import datetime, timezone
import logging
import os

app = FastAPI()

LOG_FILE = os.path.join(os.path.dirname(__file__), "visitors.log")

# 1x1 transparent GIF bytes
PIXEL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
    b"\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00"
    b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("tracker")


@app.get("/pixel.gif")
async def tracking_pixel(request: Request):
    # Respect X-Forwarded-For in case behind a proxy/nginx
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[0].strip() if forwarded else request.client.host
    user_agent = request.headers.get("user-agent", "-")
    referer = request.headers.get("referer", "-")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    logger.info("%s | IP: %s | UA: %s | Ref: %s", timestamp, ip, user_agent, referer)

    return Response(
        content=PIXEL_GIF,
        media_type="image/gif",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
    )


@app.get("/logs")
async def view_logs(n: int = 50):
    """Return the last n log lines as plain text (restrict this endpoint in prod)."""
    if not os.path.exists(LOG_FILE):
        return Response(content="No logs yet.", media_type="text/plain")
    with open(LOG_FILE) as f:
        lines = f.readlines()
    return Response(content="".join(lines[-n:]), media_type="text/plain")
