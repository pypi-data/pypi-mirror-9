__author__ = 'Frederik Diehl'


import json

def to_JSON(object):
    d = json.dumps(object, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    d = "__class__:" + str(object.__class__) + "\n" + d
    return d