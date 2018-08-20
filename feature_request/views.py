from flask import Blueprint, render_template

request_bp = Blueprint('request', __name__)


@request_bp.route("/")
def index():
    return render_template('index.html')
