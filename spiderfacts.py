import os
import time
import random

from slackclient import SlackClient

from facts import facts
from triggers import triggers


# spiderbot's ID as an environment variable
BOT_ID = os.environ.get("SPIDER_FACTS_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
# EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SPIDER_FACTS_TOKEN'))


def handle_command(command, channel):
    """
        Recieves commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "My creator has not taught me any commands."
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        This parsing function returns None unless a message contains
        a trigger keyword and was not posted by the SpiderFacts bot.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if has_trigger(output):
                return True, output['channel']
    return None, None


def has_trigger(output):
    if output:
        # make sure the bot can't trigger itself
        if 'user' in output and output['user'] != BOT_ID:
            # check if a trigger keyword was used
            if 'text' in output and any(trigger in output['text'].lower() for trigger in triggers):
                return True
    return False


def post_fact(channel):
    """
        Will only get called if a trigger word was detected.
        This function randomly selects a fact from the facts list
        and posts it to the given channel.
    """
    response = random.choice(facts)
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("SpiderBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                post_fact(channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?") 
