from flask import Flask, render_template, request
import json
import argparse
from . import postgres

app = Flask(__name__, template_folder = 'templates')

def make_response(data):
    return json.dumps({'status':'success', 'data':data})

def make_error(error):
    return json.dumps({'status':'error', 'errorMessage':error})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():
    if 'db' in request.form:
        db = request.form['db']
    else:
        db = None
    try:
        link = postgres.PostgresGateway(request.form['remotehost'], request.form['remoteport'], request.form['remoteuser'], request.form['remotepassword'], db)
    except Exception as e:
        return make_error(str(e))
    handler = getattr(link, request.form['op'], None)
    if handler != None:
        try:
            return make_response(handler(request.form))
        except IndexError as e:
            return make_error('Possible place holders in query')
        except Exception as e:
            return make_error(str(e))
    
def main():
    parser = argparse.ArgumentParser(description='PostgreSQL Query Maker')
    parser.add_argument('--ip', help='IP address on with to run the server')
    parser.add_argument('--port', help='Port to use')
    arguments = parser.parse_args()

    ip = arguments.ip if arguments.ip != None else '0.0.0.0'
    port = int(arguments.port) if arguments.port != None else 5000
    app.run(ip, port=port, debug=False)
