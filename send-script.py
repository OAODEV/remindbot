#!/usr/bin/env python
#coding: utf-8

import requests
import json
import psycopg2
import os

def main():
    hostname = os.getenv('POSTGRES_PORT_5433_TCP_ADDR', '23.236.55.11')
    port = os.getenv('POSTGRES_SERVICE_PORT', 5433)
    host = '%s:%s' % (hostname, port)
    database = "remindbot"
    user = "thomas"
    with open('/secret/pgpassword', 'r') as pwf:
        password = pwf.read().strip()
    try:
        with open('/secret/hookurl', 'r') as hookf:
            url = hookf.read().strip()
    except:
        url = "https://hooks.slack.com/services/G02594UC0/O081ERH01/O081ERH01O081ERH01" # <- changeme ;)

    conn = psycopg2.connect(host=hostname,
                            port=port,
                            database=database,
                            user=user,
                            password=password)
    cur = conn.cursor()
    sql = """
            update reminder
               set sent_flag = true
             where trigger_dt <= now()
               and not sent_flag
         returning reminder_task,
                   channel_name,
                   username,
                   user_code;
          """
    cur.execute(sql)
    results = cur.fetchall()
    for row in results:
        task = row[0]
        channel = u'#%s' % row[1]
        name = row[2]
        user = row[3]
        r = 'Hey, <@%s|%s> asked me to remind <!channel> to %s' % (user,
         name, task)
        payload = {'text': r, 'channel': channel}
        print json.dumps(payload)
        rq = requests.post(url, data=json.dumps(payload))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
