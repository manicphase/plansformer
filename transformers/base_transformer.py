import html
from helpers.object_searcher import ObjectSearcher, AdvancedObjectSearcherResult
import re
from bs4 import BeautifulSoup

class TransformerResultBundle():
    def __init__(self, tree, content_object: AdvancedObjectSearcherResult, link):
        self.tree = tree
        self.content_object = content_object
        self.link = link

class BaseTransformer():
    def __init__(self, response_data):
        self.response_data = response_data
        self.target_sites = []

    def get_content_objects(self):
        searcher = ObjectSearcher(self.response_data)
        self.content_objects = searcher.list_by_key("content")

    def get_relevant_contents(self):
        self.get_content_objects()
        search_string = "{}".format("|".join(self.target_sites))
        relevant_objects = []
        for ro in self.content_objects:
            match = re.search(search_string, str(ro))
            if match:
                relevant_objects.append([ro, match.group(0)])
        return relevant_objects

    def get_html_nodes_for_content(self, content_object, match):
        tree = BeautifulSoup(str(content_object), "html.parser")
        links = [t for t in tree.findAll("a") if t.attrs.get("href","").startswith(str(match))]
        return tree, links

    def get_all_nodes(self):
        relevant_content = self.get_relevant_contents()
        results = {}
        for rc in relevant_content:
            tree, links = self.get_html_nodes_for_content(rc[0], rc[1])
            if rc[0] in results:
                results[rc[0]]["links"].append(rc[1])
            else: 
                results[rc[0]] = {"tree": tree, "links":links}
        return results

    def transform_one(self, link):
        raise NotImplementedError

    def transform(self):
        all_nodes = self.get_all_nodes()
        for json_node in all_nodes:
            for link in all_nodes[json_node]["links"]:
                bundle = TransformerResultBundle(all_nodes[json_node]["tree"], json_node, link)
                result = self.transform_one(bundle)            
                link.replace_with(result)
            json_node.set(html.unescape(str(all_nodes[json_node]["tree"])))