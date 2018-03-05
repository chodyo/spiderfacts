import sys, os, time, random, json

from slackclient import SlackClient


# spiderbot's attributes
class SpiderFacts:
    def __init__(self):
        self.NAME = 'spiderfacts'
        self.TOKEN = os.environ['SPIDER_FACTS_TOKEN']
        self.CLIENT = SlackClient(self.TOKEN)
        self.ID = self.get_id()
        # load facts and triggers
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        data = json.load(open(os.path.join(data_dir, 'data.json')))
        self.facts = data.get("facts")
        self.triggers = data.get("triggers")


    def get_id(self):
        """
            Gets the ID of the spiderbot from Slack. Will use this ID so the bot
            doesn't trigger messages off itself.
        """
        api_call = self.CLIENT.api_call("users.list")
        if api_call.get('ok'):
            # retrieve all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if user.get('name') == self.NAME:
                    return user.get('id')
            raise Exception(f"No bot user named {self.NAME} in your slack channel.")
        else:
            raise Exception("error connecting to slack API:", api_call['error'])


    def run(self):
        if not self.ID:
            raise ValueError("Bot ID not set.")
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if self.CLIENT.rtm_connect():
            print(f"{self.NAME} connected and running! spinning webs now..")
            while True:
                command, channel = self.parse_slack_output(self.CLIENT.rtm_read())
                if command and channel:
                    self.post_fact(channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            raise Exception("Connection failed. Invalid Slack token or bot ID?")


    def parse_slack_output(self, output_list):
        """
            The Slack Real Time Messaging API is an events firehose.
            This parsing function returns None unless a message contains
            a trigger keyword and was not posted by the SpiderFacts bot.
        """
        if output_list and len(output_list) > 0:
            for output in output_list:
                if self.has_trigger(output):
                    return True, output['channel']
        return None, None


    def has_trigger(self, output):
        if output:
            # make sure the bot can't trigger itself
            if 'user' in output and output['user'] != self.ID:
                # check if a trigger keyword was used
                if 'text' in output and any(trigger in output['text'].lower() for trigger in self.triggers):
                    return True
        return False


    # def handle_command(self, command, channel):
    #     """
    #         Recieves commands directed at the bot and determines if they
    #         are valid commands. If so, then acts on the commands. If not,
    #         returns back what it needs for clarification.
    #     """
    #     response = "My creator has not taught me any commands."
    #     self.CLIENT.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


    def post_fact(self, channel):
        """
            Will only get called if a trigger word was detected.
            This function randomly selects a fact from the facts list
            and posts it to the given channel.
        """
        fact = random.choice(self.facts)
        api_call = self.send_message(channel, fact)
        if api_call.get('ok'):
            print(f"sent fact: {fact[:30]}...")
        else:
            raise Exception("could not send fact:", api_call['error'])

    def send_message(self, channel, text):
        tries = 0
        sent = False
        response = None
        while tries < 3 and not sent:
            response = self.CLIENT.api_call("chat.postMessage", channel=channel, text=text, as_user=True)
            tries += 1
            sent = response.get('ok')
        return response

if __name__ == "__main__":
    bot = SpiderFacts()
    bot.run()
