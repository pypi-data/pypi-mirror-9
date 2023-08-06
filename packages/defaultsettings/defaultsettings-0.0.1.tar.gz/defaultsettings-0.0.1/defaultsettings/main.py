try: import simplejson as json
except ImportError: import json

class Settings(object):
    def __init__(self):
        self.defaults = {}
        self.data = {}

    def default(self, key, value):
        self.defaults[key] = value
        self.data[key] = value

    def serialize(self):
        return json.dumps(self.data, indent=2, sort_keys=True)
    
    def save(self, filename):
        json_data = self.serialize()
        with open(filename, "w") as f:
            f.write(json_data)
    
    def load(self, filename):
        data = {}
        with open(filename, "r") as f:
            data = json.loads(f.read())
        for k,v in data.items():
            if k not in self.defaults:
                raise KeyError("Key not recognized [%s]"%(k))
            self.data[k] = v
    def default(self, key, value):
        self.defaults[key] = value
        self.data[key] = value

    def serialize(self):
        return json.dumps(self.data, indent=2, sort_keys=True)
    
    def save(self, filename):
        json_data = self.serialize()
        with open(filename, "w") as f:
            f.write(json_data)
    
    def load(self, filename):
        data = {}
        
        with open(filename, "r") as f:
            data = json.loads(f.read())
        for k,v in data.items():
            if k not in self.defaults:
                raise KeyError("Key not recognized [%s]"%(k))
            self.data[k] = v
