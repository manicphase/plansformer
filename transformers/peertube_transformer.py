from transformers.base_transformer import BaseTransformer, TransformerResultBundle

target_sites = ["https://video.manicphase.me","https://diode.zone","https://tilvids.com","https://videos.trom.tf"]

class PeertubeTransformer(BaseTransformer):
    def __init__(self, response_data):
        super(PeertubeTransformer, self).__init__(response_data)
        self.target_sites = self.target_sites + [ts+"/w/" for ts in target_sites]

    def transform_one(self, result: TransformerResultBundle):
        template = open("templates/peertube_video_embed.html").read()
        new_embed_link = result.link.attrs["href"].replace("/w/", "/videos/embed/")
        result = template.format(new_embed_link)
        print(result)
        return result