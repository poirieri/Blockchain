from json import JSONEncoder
import json
from MinimalBlock import MinimalChain


class aBlockEncoder(JSONEncoder):

    def default(self, object):

        if isinstance(object, MinimalChain):

            return object.__dict__

        else:

            return json.JSONEncoder.default(self, object)