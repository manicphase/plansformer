class ObjectSearcherResult():
    def __init__(self, json_obj, root, key, path):
        self.json_obj = json_obj
        self.key = key
        self.path = path
        self.root = root
        print(path)
        
    def __repr__(self):
        return self.json_obj[self.key]

    def __contains__(self, value):
        return self.json_obj[self.key].__contains__(value)

    def delete(self):
        #del self.json_obj[0]
        location = self.root
        for node in self.path:      
            if type(node) == int:
                if location[node]:
                    del location[node]
                break
            location = location[node]

    def delete_card(self):
        location = self.root
        try:
            for node in self.path:
                if type(location) != list:
                    if "card" in location.keys():
                        del location["card"]
                        break
                location = location[node]
        except:
            pass
            

    def split(self, value = None):
        return self.json_obj[self.key].split(value)
    
    def set(self, value):
        self.json_obj[self.key] = value


class ObjectSearcher():
    def __init__(self, json_obj):
        self.json_obj = json_obj
        
    def _search(self, obj, key, path=None):
        if not path: path = []
        path = path[:]
        if type(obj) == list:
            for i in range(len(obj)):
                _path = path[:]
                _path.append(i)
                self._search(obj[i], key, _path)
        if type(obj) == dict:
            for k,v in obj.items():
                if k == key:
                    if type(v) == self.by_type:
                        _path = path[:]
                        _path.append(k)
                        self.results.append(ObjectSearcherResult(obj, self.json_obj, key, _path))
                elif type(v) == dict:
                    _path = path[:]
                    _path.append(k)
                    self._search(v, k, _path)
                elif type(v) == list:
                    self._search(v, key, path)

        
    def list_by_key(self, key, by_type=str):
        self.results = []
        self.by_type = by_type
        self._search(self.json_obj,key)
        return self.results
        