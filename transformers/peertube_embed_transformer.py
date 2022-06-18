from transformers import instance_urls
from transformers.base_transformer import BaseTransformer, TransformerResultBundle


class PeertubeEmbedTransformer(BaseTransformer):
    def __init__(self, response_data):
        super(PeertubeEmbedTransformer, self).__init__(response_data)
        self.target_sites = self.target_sites + [ts+"/w/" for ts in + instance_urls.peertube_instances]

    def transform_one(self, result: TransformerResultBundle):
        template = open("templates/peertube_video_embed.html").read()
        new_embed_link = result.link.attrs["href"].replace("/w/", "/videos/embed/")
        result = template.format(new_embed_link)
        print(result)
        return result