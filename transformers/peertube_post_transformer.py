import html
import re
from transformers.base_transformer import BaseTransformer, TransformerResultBundle
from bs4 import BeautifulSoup

target_sites = ["https://video.manicphase.me","https://diode.zone","https://tilvids.com","https://videos.trom.tf"]

class PeertubePostTransformer(BaseTransformer):
    def __init__(self, response_data):
        super(PeertubePostTransformer, self).__init__(response_data)
        self.target_sites = self.target_sites + target_sites

    def get_relevant_contents(self):
        self.get_content_objects()
        search_string = "{}".format("|".join(self.target_sites))
        relevant_objects = []
        for ro in self.content_objects:
            ro.parent["account"]["url"]
            match = re.search(search_string, ro.parent["account"]["url"])
            if match:
                relevant_objects.append([ro, match.group(0)])
        return relevant_objects

    def get_all_nodes(self):
        relevant_content = self.get_relevant_contents()
        results = []
        for rc in relevant_content:
            tree = BeautifulSoup(str(rc[0]), "html.parser")
            results.append([rc[0], tree])
        return results

    def transform(self):
        all_nodes = self.get_all_nodes()
        for json_node in all_nodes:
            node, tree = json_node
            original_path = node.parent["media_attachments"][0]["remote_url"]
            video_id = original_path.split("/hls/")[1].split("/")[0]
            template = open("templates/peertube_video_embed.html").read()
            new_embed_link = "https://" + original_path.split("/")[2] + "/videos/embed/" + video_id
            title_node = tree.find_all("a")[0]
            title_node.insert_after(template.format(new_embed_link))
            node.set(html.unescape(str(tree)))
            del node.parent["media_attachments"]
            json_node.set(html.unescape(str(all_nodes[json_node]["tree"])))