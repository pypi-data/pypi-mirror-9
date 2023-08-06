import json
import requests

BASE_URL = "https://push.ducksboard.com/v/%d"


class Mallard(object):

    def __init__(self, api_key, widgets=None):
        self.widgets = {}
        self.api_key = api_key

        if widgets:
            for (name, widget_id) in list(widgets.items()):
                self.register_widget(name, widget_id)

    def register_widget(self, name, widget_id):
        if name in self.widgets:
            raise KeyError("A widget named %s is already registered" % name)

        self.widgets[name] = widget_id

    def push(self, **kwargs):
        widget_id = kwargs.pop("widget_id", None)
        if not widget_id:
            name = kwargs.pop("name", None)
            if name:
                widget_id = self.widgets.get(name, None)

        if not widget_id:
            raise ValueError("You need to specify widget_id or name to push")

        encoded_data = json.dumps(kwargs)
        res = requests.post(BASE_URL % widget_id,
                            auth=(self.api_key, 'x'),
                            data=encoded_data)
        return res.status_code == 200
