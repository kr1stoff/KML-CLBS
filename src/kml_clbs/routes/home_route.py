from flask import Blueprint, render_template

from kml_clbs.models.db import get_db

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    db = get_db()
    return render_template('index.html')
