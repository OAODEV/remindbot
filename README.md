#Remindbot
[![badge](https://circleci.com/gh/OAODEV/remindbot.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/OAODEV/remindbot)

NB: as of 2015-11-05, this is covered by built-in functionality in Slackbot `/remind` command. It's been fun, but I won't be developing this further.

`/cue us in 40 minutes to empty the trash`

Send Slackbot-style reminders to a public Slack channel, using a Slash Command and Incoming Webhook

- We use `/cue` slash command to prevent confusion with standard `/reminder` command. You can set that up as you prefer.
- The app saves reminder queue in a Postgres table. SQL to create that included, but no fancy ORMs here ;)
- Needs a Slack API token, for checking user timezone
- CherryPy server included; just build and run a container using included Dockerfile, or `python remindbot.py` if running without containerizing.
- Example crontab file included; checks every minute for pending reminders to send to Incoming Webhook.
- Incoming reminder messages appear in format "Hey, $person asked me to remind @channel to $message"


![Screenshot of reminder](https://s3-us-west-2.amazonaws.com/shots-tym/hold/Screen+Shot+2015-07-25+at+09.19.11.png)
