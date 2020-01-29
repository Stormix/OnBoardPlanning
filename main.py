#!flask/bin/python
from flask import Flask, make_response, request, jsonify, abort
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
from src import Extractor
from flask import send_file
import os

load_dotenv()
auth = HTTPBasicAuth()
app = Flask(__name__)


@auth.verify_password
def verify_password(username, password):
    return password == os.getenv("API_PASSWORD")


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.route('/')
@auth.login_required
def index():
    return "Hello, World!"


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/extract', methods=['POST'])
def extract():
    print(request.json)
    if not request.json or not 'name' in request.json  or not 'username' in request.json or not 'password' in request.json:
        abort(400)
    name = request.json['name']
    username = request.json['username']
    password = request.json['password']
    filename = username+".ics"
    e = Extractor(name, username, password)
    e.delay = 2
    e.launchBrowser() # TODO debug headless mode
    e.login()
    e.goToPlanning()
    e.goToSchedule()
    e.displayMonth()
    path = e.monthPlanning(filename)
    e.browser.close()
    try:
      return send_file(path, attachment_filename=filename)
    except Exception as e:
      return str(e)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3333)


# 
# from src import Planner

# name = os.getenv("NAME")
# email = os.getenv("EMAIL")
# password = os.getenv("PASSWORD")
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# CREDENTIALS_FILE = 'auth/client_secret.json'



# p = Planner(SCOPES, CREDENTIALS_FILE)
# p.importPlanning("downloads/planning.ics")
