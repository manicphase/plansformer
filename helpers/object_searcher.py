from pprint import pprint

class ObjectSearcherResult():
    def __init__(self, parent, root, key, path):
        self.parent = parent
        self.key = key
        self.path = path
        self.root = root
        print(path)
        
    def __repr__(self):
        return self.parent[self.key]

    def __contains__(self, value):
        return self.parent[self.key].__contains__(value)

    def delete(self):
        location = self.root
        for node in self.path:      
            if type(node) == int:
                if location[node]:
                    del location[node]
                break
            location = location[node]

    def _delete_sibling(self, tag):
        print("DELETE", tag, self.path)
        if not self.path:
            try:
                del self.root[tag]
            except:
                pass
        location = self.root
        try:
            for node in self.path:
                if type(location) != list:
                    if tag in location.keys():
                        print("DELETING", location[tag])
                        del location[tag]
                        break
                location = location[node]
        except:
            pass
    
    def delete_card(self):
        self._delete_sibling("card")

    def delete_media(self):
        self._delete_sibling("media_attachments")
            

    def split(self, value = None):
        return self.parent[self.key].split(value)
    
    def set(self, value):
        self.parent[self.key] = value

class AdvancedObjectSearcherResult(ObjectSearcherResult):
    def __init__(self, parent, root, key, path):
        super(AdvancedObjectSearcherResult, self).__init__(parent, root, key, path)

    def get_original_poster(self):
        if self.parent.get("reblog"):
            return self.parent["reblog"]["account"]["url"]
        else:
            return self.parent["account"]["url"]

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
                        self.results.append(AdvancedObjectSearcherResult(obj, self.json_obj, key, _path))
                elif type(v) == dict:
                    _path = path[:]
                    _path.append(k)
                    self._search(v, k, _path)
                elif type(v) == list:
                    self._search(v, key, path)

        
    def list_by_key(self, key, by_type=str):
        if type (self.json_obj) != list:
            if key in self.json_obj.keys():
                return [AdvancedObjectSearcherResult(self.json_obj, self.json_obj, key, [])]
        self.results = []
        self.by_type = by_type
        self._search(self.json_obj,key)
        return self.results
        