from flask import Flask
from datetime import timedelta

app = Flask(__name__)
app.config.from_object('config')
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=1)
from app import views
