from urllib.parse import urlencode
from urllib.request import Request, urlopen


class Slacking():

    def __init__(self, message, webhook, channel='#general', username='Slacking'):
        self.username = username
        self.message = message
        self.webhook = webhook

        if channel[0] != '#':
            self.channel = '#' + channel
        else:
            self.channel = channel

    def send_json_to_slack(self):

        payload_string = ''

        try:
            for item in self.message.items():
                label, message = item

                payload_string += '%s: %s, ' % (label, message)
        except AttributeError:
            print('Error: In order to send json, '
                  'the message must be a dictionary')
            return None

        payload_string = payload_string[:-2]

        payload_dict = '{ "channel": "%s", "username": "%s", "text": "%s" }' % (self.channel, self.username, payload_string)

        data = urlencode({'payload': payload_dict})

        data = data.encode('utf-8')
        request = Request(self.webhook)
        request.add_header("Content-Type",
                           "application/x-www-form-urlencoded;charset=utf-8")

        f = urlopen(request, data)

        return f

    def send_message_to_slack(self):

        payload_dict = '{ "channel": "%s", "username": "%s", "text": "%s" }' % (self.channel, self.username, self.message)

        data = urlencode({'payload': payload_dict})

        data = data.encode('utf-8')
        request = Request(self.webhook)
        request.add_header("Content-Type",
                           "application/x-www-form-urlencoded;charset=utf-8")

        f = urlopen(request, data)

        return f
