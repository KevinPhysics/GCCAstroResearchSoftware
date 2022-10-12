from flask import Flask

from starSelectGraphic import main as selectStar
from createSchedule import writeSchedule

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False

from app import routes