from flask import Flask

app = Flask(__name__)
import ssg_reloader.views

