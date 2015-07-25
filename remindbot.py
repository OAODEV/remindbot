#!/usr/bin/env/ python
# coding: utf-8

from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
import json
import psycopg2
import slack
import slack.users
from datetime import datetime
from pytz import timezone
import pytz
import os
import parsedatetime as pdt
import cherrypy
from paste.translogger import TransLogger

app = Flask(__name__)
api = Api(app)

# Database connection config
# TODO: move to yaml file
hostname = os.getenv('POSTGRES_PORT_5433_TCP_ADDR', 'localhost')
port = os.getenv('POSTGRES_SERVICE_PORT', 5433)
host = '%s:%s' % (hostname, port)
database = "remindbot"
user = "thomas"
try:
    with open('/secret/pgpassword', 'r') as pwf:
        password = pwf.read().strip()
except:
    password = 'Password123' # ;)

class RemindUs(Resource):
    def post(self):
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('channel_id', type=unicode)
        parser.add_argument('channel_name', type=unicode)
        parser.add_argument('token', type=unicode)
        parser.add_argument('text', type=unicode)
        parser.add_argument('user_id', type=unicode)
        parser.add_argument('user_name', type=unicode)
        args = parser.parse_args()
        channel = args.channel_name
        channel_id = args.channel_id
        user_id = args.user_id
        user_name = args.user_name
        token = args.token
        reminder = args.text.split(' to ', 1)

        # Get user timezone from Slack API
        # TODO: tokens should also be in seperate secret config
        try:
            with open('/secret/apitoken', 'r') as apitokenf:
                slack.api_token = apitokenf.read().strip()
        except:
            slack.api_token = 'a2JrYy0yMTc5MTUzNzgyLTMyMjI2NDE4Mj' # <- fake

        user_tz = timezone(slack.users.info(user_id)['user']['tz'])

        # Parse date from reminder text
        p = pdt.Calendar()
        utc = timezone('UTC')
        trigger = p.parseDT(reminder[0])[0]

        # Localize time zone
        # Natural intervals ('in 10 mins') as utc
        if "in" in reminder[0].split():
            trigger_dt = utc.localize(trigger)
        # Otherwise user's local time ('at 10:00am')
        else:
            trigger_dt = user_tz.localize(trigger)

        try:
            with open('/secret/token', 'r') as tokenf:
                valid = tokenf.read().strip()
        except:
            valid = "REJJYXFGWFhwUzBlMFhHUVR" # <- phony ;)

        #Only accept posts from our team
        if token != valid:
            return ('naughty, naughty!', 403)

        # won't work in direct messages
        elif channel == 'directmessage':
            return(u'Whoops, only works in a public channel. Sorry :(', 200)
        # confirm parsing
        elif len(reminder) != 2 or trigger_dt <= datetime.utcnow().replace(tzinfo = pytz.utc):
            return 'Whoops! Please enter reminders in the form: /remind us in 40 minutes to empty the trash'

        else: # Save the reminder!
            task = reminder[1].strip()
            conn = psycopg2.connect(host=hostname,
                                    port=port,
                                    database=database,
                                    user=user,
                                    password=password)
            cur = conn.cursor()
            sql = """
                      insert into reminder(reminder_task,
                                           trigger_dt,
                                           channel_code,
                                           channel_name,
                                           username,
                                           user_code)
                      values (%s, %s, %s, %s, %s, %s);
                  """
            cur.execute(sql, (task, trigger_dt, channel_id,
                channel, user_name, user_id))
            conn.commit()
            conn.close()
            # Let the user know
            # TODO: Friendlier date formatting
            return ('OK, I will remind #%s to %s at %s' % (channel, task,
                trigger_dt.astimezone(user_tz)), 200)


api.add_resource(RemindUs, '/')

def run_server():
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload.on': True,
        'environment': 'embedded',
        'log.screen': True,
        'server.socket_port': 5001,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    run_server()

# Uncomment below (and comment out above ) for Flask dev/test server
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5001)