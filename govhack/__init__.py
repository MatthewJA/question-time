from flask import Flask, url_for, redirect

import assets

app = Flask(__name__, instance_relative_config=True)


assets.register_assets(app)


import govhack.views