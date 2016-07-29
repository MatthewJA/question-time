from flask import Flask, url_for, redirect

app = Flask(__name__, instance_relative_config=True)

import govhack.views