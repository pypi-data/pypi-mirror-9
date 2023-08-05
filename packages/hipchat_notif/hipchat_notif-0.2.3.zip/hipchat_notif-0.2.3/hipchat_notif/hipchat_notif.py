#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'drogov'

import requests
import json
from .error import *

__all__ = ["HipchatNotificator"]


class Hipchat(object):
    def __init__(self, token, apiversion=1):
        if apiversion == 1:
            self.apiurl = "https://api.hipchat.com/v1"
            if token and token != "":
                self.token = token
            else:
                raise HipchatAuthError(message="Error: token is null.")
            self._test_token()
            self.admin = False
        else:
            raise HipchatError("Unknown API version")

    def _test_token(self):
        """
            Validation TOKEN.
        """

        url = "{}/rooms/list?auth_token={}&auth_test=true".format(self.apiurl, self.token)
        code, content = self._send_requests(url)
        result = json.loads(content.decode('utf-8'))
        notif_message = "This auth token does not have access to this method. Please see: https://www.hipchat.com/docs/api/auth"
        if code == 202:
            self.admin = True
        elif code == 401 and result["error"]["message"] == notif_message:
            self.admin = False
        else:
            raise HipchatAuthError(401, result["error"]["message"])

    def _send_requests(self, url, param=None):
        try:
            if param == None:
                result = requests.get(url)
            else:
                result = requests.post(url, data=param)
        except requests.RequestException as error:
            pass
        return result.status_code, result._content

    def _get_room(self, room):
        return room if room != None else self.room

    @property
    def room(self):
        return self._room

    @room.setter
    def room(self, value):
        self._room = value

    @property
    def notification_name(self):
        return self._notification_name

    @notification_name.setter
    def notification_name(self, value):
        """
        Notification Name
        Required.
        Name the message will appear be sent from.


        :param value: Must be less than 15 characters long.
        May contain letters, numbers, -, _, and spaces.
        """
        self._notification_name = value


    def send_message(self, message, room=None, notify=0, message_format="html", color="yellow"):
        """
        Send message to hipchat API.
        :param message: Required. The message body. 10,000 characters max.
        :param room: Room ID or name
        :param notify:
        :param message_format: Determines how the message is treated by our server and rendered inside HipChat applications.
                html - Message is rendered as HTML and receives no special treatment. Must be valid HTML and entities must be escaped (e.g.: &amp; instead of &). May contain basic tags: a, b, i, strong, em, br, img, pre, code, lists, tables. Special HipChat features such as @mentions, emoticons, and image previews are NOT supported when using this format.
                text - Message is treated just like a message sent by a user. Can include @mentions, emoticons, pastes, and auto-detected URLs (Twitter, YouTube, images, etc).
        :param color: Background color for message. One of "yellow", "red", "green", "purple", "gray", or "random". (default: yellow)
        """
        url = "{}//rooms/message?format=json&auth_token={}".format(self.apiurl, self.token)
        data = {
            "room_id": self._get_room(room),
            "from": self.notification_name,
            "notify": notify,
            "message": message,
            "message_format": message_format,
            "color": color
        }

        code, content = self._send_requests(url, data)
        result = json.loads(content.decode('utf-8'))
        if code == 200:
            return
        elif code == 404:
            raise HipchatRoomError(404, result["error"]["message"])
        elif code == 400:
            raise HipchatMessageError(400, result["error"]["message"])
        else:
            raise HipchatError(result["error"]["code"], result["error"]["message"], result["error"]["type"])


class HipchatNotificator(Hipchat):
    """
        Sending of predefined messages.
    """

    def notif(self, message, notify=1, message_format="html"):
        data = {
            "notify": notify,
            "message": message,
            "message_format": message_format,
            "color": "gray"
        }
        self.send_message(**data)

    def alert(self, message, notify=1, message_format="html"):
        data = {
            "notify": notify,
            "message": "<strong>{}</strong>".format(message),
            "message_format": message_format,
            "color": "red"
        }
        self.send_message(**data)


    def ok(self, message, notify=0, message_format="html"):
        data = {
            "notify": notify,
            "message": message,
            "message_format": message_format,
            "color": "green"
        }
        self.send_message(**data)

    def message(self, message, notify=0, message_format="html"):
        data = {
            "notify": notify,
            "message": message,
            "message_format": message_format,
            "color": "yellow"
        }

        self.send_message(**data)
