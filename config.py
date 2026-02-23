import os

SERIAL_PORT = os.environ.get("MESHCORE_SERIAL_PORT", "/dev/ttyV0")
SERIAL_BAUD = int(os.environ.get("MESHCORE_SERIAL_BAUD", "115200"))
SERIAL_TIMEOUT = float(os.environ.get("MESHCORE_SERIAL_TIMEOUT", "5"))

POLL_INTERVAL_SECS = int(os.environ.get("MESHCORE_POLL_INTERVAL", "300"))

DB_PATH = os.environ.get("MESHCORE_DB_PATH", os.path.join(os.path.dirname(__file__), "meshcore.db"))
RETENTION_DAYS = int(os.environ.get("MESHCORE_RETENTION_DAYS", "30"))

FLASK_HOST = os.environ.get("MESHCORE_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("MESHCORE_PORT", "5000"))
FLASK_DEBUG = os.environ.get("MESHCORE_DEBUG", "0") == "1"

MAX_QUERY_HOURS = 720  # 30 days
