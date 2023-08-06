import requests


class HubbleData(object):
    def __init__(self, value, column, label):
        self.value = value
        self.column = column
        self.label = label

        # TODO
        # high
        # low

        # TODO multiple screen?
        # screen

        # If poll, not value
        # poll_url      - the url of the web request
        # poll_seconds  - how often to poll for data changes
        # poll_failed   - the message to display if the request fails
        # poll_method   - the method to apply to the result for displaying (accepts one of the below values)
            # count_array             - if the endpoint is an array, counts the list
            # json_value:{expression} - this will select a single json value from the response. some samples
                                          # of this are in the Github Dashboard below. visit
                                          # https://github.com/dfilatov/jspath for a full reference.
                                          # poll_header   - any headers to add to the request (you can specify more than one poll_header if you need to)

    def as_dict(self):
        return self.__dict__

    def is_valid(self, data):
        return True


class Hubble(object):
    HTTP_OK = 200
    DEFAULT_URL = 'http://localhost:9999'

    def __init__(self, url=None):
        self.url = url or self.DEFAULT_URL

    def send(self, data):
        if not data:
            return False

        valid_data = data
        if not isinstance(data, HubbleData):
            valid_data = HubbleData(**data)

        response = requests.post(
            self.url,
            data=valid_data.as_dict()
        )

        if response.status_code != self.HTTP_OK:
            raise requests.exceptions.ConnectionError(
                'The connection is not HTTP 200 OK'
            )

    def increment(self, label, column=0):
        data = HubbleData(label=label, column=column, value='increment')
        self.send(data)

    def decrement(self, label, column=0):
        data = HubbleData(label=label, column=column, value='decrement')
        self.send(data)
