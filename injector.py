import configparser
from pprint import pprint
from flask import request, Response, Flask
import requests
import json
from helpers.object_searcher import ObjectSearcher
from helpers.security_header_handler import SecurityHeaderHandler
from transformers import transformers

app = Flask(__name__, static_folder=None)

config = configparser.RawConfigParser()
config.read("config.conf")
homeurl = config["home"]["homeurl"]

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    print(request.url.replace(request.host_url, homeurl))
    data = request.get_data()
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, homeurl),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=data,
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)

    shh = SecurityHeaderHandler(response.headers)
    shh.add_source("child-src", "https://manicphase.me")
    shh.add_source("child-src", "https://tilvids.com")

    response.headers = shh.headers

    def fold_statuses(results):
        if len(results) < 2:
            return results
            
        i = len(results) -1
        while i > 0:
            if results[i-1].json_obj["account"]["acct"] == results[i].json_obj["account"]["acct"]:
                results[i-1].set(str(results[i]) + "<hr>" + str(results[i-1]))
                results[i].delete() 
                del(results[i]) 
            i -= 1


    if ("statuses" in path) or ("timelines" in path):
        jdata = json.loads(response.data)
        if jdata:
            for t in transformers:
                t(jdata).transform()                    

            searcher = ObjectSearcher(jdata)
            results = searcher.list_by_key("content")
            if not "accounts" in path:
                fold_statuses(results)

            response.data = str.encode(json.dumps(jdata))
    return response

app.run(host='0.0.0.0', port=8182, debug=True, threaded=True)