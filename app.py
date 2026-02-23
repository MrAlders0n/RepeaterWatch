import logging
import signal
import sys

from flask import Flask

import config
from database.schema import init_db
from database import models
from api.routes import api
from collector.stats_poller import StatsPoller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    # Initialize database
    init_db(config.DB_PATH)
    models.init(config.DB_PATH)

    # Register API blueprint
    app.register_blueprint(api)

    # Root route serves dashboard
    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    # Start collector
    poller = StatsPoller()
    app.config["poller"] = poller
    poller.start()

    def shutdown_handler(signum, frame):
        logger.info("Shutting down collector...")
        poller.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        use_reloader=False,
    )
