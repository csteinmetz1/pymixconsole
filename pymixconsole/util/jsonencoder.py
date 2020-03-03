import json
import numpy as np

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return super(CustomJSONEncoder, self).encode(bool(obj))

        return super(CustomJSONEncoder, self).default(obj)