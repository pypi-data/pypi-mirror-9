# coding: utf-8

from __future__ import print_function
from slacky import Slacky
from websocket import create_connection


token = 'xoxp-2623518012-2623518014-3375529141-0ac785'
slacky = Slacky(token=token)


class Server(object):
    def __init__(self, slack):
        """ 'data' is returned json data by https://api.slack.com/methods/rtm.start
        """
        self.domain = None
        self.reply_json = None
        self.slack = slack
        self.username = None
        self.websocket = None
        self.channels = []  # list of channel objects.
        self.groups = []    # list of group objects.
        self.ims = []       # list of ims objects.

    def connect(self):
        reply = self.slack.rtm.start
        if reply.status_code != 200:
            raise SlackConnectionError
        else:
            reply_json = reply.json()
            if reply_json['ok']:
                self.parse_slack_json(reply_json)

    def parse_slack_json(self, json_data):
        self.reply_json = json_data.copy()
        self.domain = self.reply_json['team']['domain']
        self.username = self.reply_json['self']['name']
        try:
            self.websocket = create_connection(self.reply_json['url'])
            self.websocket.sock.setblocking(0)
        except:
            raise SlackWebsocketConnectionError

    def parse_channel_data(self, channels):
        pass


class SlackConnectionError(Exception):
    pass


class SlackWebsocketConnectionError(Exception):
    pass


class Channel(object):
    def __init__(self, server, name, id, members=[]):
        self.server = server
        self.name = name
        self.id = id
        self.members = members

    def __eq__(self, compare_str):
        if self.name == compare_str or self.id == compare_str:
            return True
        return False

    def __str__(self):
        data = ""
        for key in self.__dict__.keys():
            data += "{} : {}\n".format(key,  str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

    def send_message(self):
        pass


server = Server(slacky)
