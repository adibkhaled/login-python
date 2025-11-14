from flask import Flask
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
app.logger.setLevel(logging.INFO)

# register blueprints after app creation
from src.login import bp as login_bp
from src.logout import bp as logout_bp
from src.license import bp as licence_bp

app.register_blueprint(login_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(licence_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", 5010)))
    debug = os.environ.get("FLASK_ENV", "").lower() == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)