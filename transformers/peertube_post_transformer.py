import html
import re
from transformers import instance_urls
from transformers.base_transformer import BaseTransformer, TransformerResultBundle
from bs4 import BeautifulSoup



class PeertubePostTransformer(BaseTransformer):
    def __init__(self, response_data):
        super(PeertubePostTransformer, self).__init__(response_data)
        self.target_sites = self.target_sites + instance_urls.peertube_instances

    def get_relevant_contents(self):
        self.get_content_objects()
        search_string = "{}".format("|".join(self.target_sites))
        relevant_objects = []
        for ro in self.content_objects:
            match = re.search(search_string, ro.get_original_poster())
            if match:
                relevant_objects.append([ro, match.group(0)])
        return relevant_objects

    def get_all_nodes(self):
        relevant_content = self.get_relevant_contents()
        results = []
        for rc in relevant_content:
            tree = BeautifulSoup(str(rc[0]), "html.parser")
            if rc[0].parent.get("media_attachments"):
                results.append([rc[0], tree])
        return results

    def construct_embed(self, tree, video_url):
        newtag = tree.new_tag('iframe')
        newtag.attrs["title"] = ""
        newtag.attrs["src"] = video_url
        newtag.attrs["allowfullscreen"] = "" 
        newtag.attrs["sandbox"] = "allow-same-origin allow-scripts allow-popups" 
        newtag.attrs["width"] = "100%" 
        newtag.attrs["height"] = "315" 
        newtag.attrs["frameborder"] ="0"
        return newtag


    def transform(self):
        all_nodes = self.get_all_nodes()
        for json_node in all_nodes:
            node, tree = json_node

            original_path = node.parent["media_attachments"][0]["remote_url"]
            print(original_path)
            if "/hls/" in original_path:
                video_id = original_path.split("/hls/")[1].split("/")[0]
            elif "/watch/" in original_path:
                video_id = original_path.split("/watch/")[1].split("/")[0]
                original_path = tree.find_all("a")[0].attrs["href"].split("/")[2]
            template = open("templates/peertube_video_embed.html").read()
            new_embed_link = "https://" + original_path.split("/")[2] + "/videos/embed/" + video_id
            title_node = tree.find_all("a")[0]
            #title_node.insert_after(template.format(new_embed_link))
            newtag = self.construct_embed(tree, new_embed_link)
            title_node.insert_after(newtag)
            print("###################")
            print(tree)
            try:
                node.delete_media()
            except:
                pass
            node.set(html.unescape(str(tree)))
            try:
                node.parent["reblog"]["content"] = str(tree)
                del node.parent["reblog"]["media_attachments"] # TODO: make this bit better
            except: pass

        return