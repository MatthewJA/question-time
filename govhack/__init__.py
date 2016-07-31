from flask import Flask, url_for, redirect

from . import assets
from .database import db_session
from . import models

app = Flask(__name__, instance_relative_config=True)

assets.register_assets(app)

import govhack.views


@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()