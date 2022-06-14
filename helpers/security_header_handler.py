class SecurityHeaderHandler():
    def __init__(self, headers):
        self.headers = headers
        header_list = [h.split(" ",1) for h in headers.get("content-security-policy").split(";")]
        header_dict = {h[0]:h[1:] for h in header_list}
        for k,v in header_dict.items():
            if v:
                header_dict[k] = v[0].split(" ")
        self.header_dict = header_dict

    def rebuild_headers(self):
        csp_string = ";".join(["{} {}".format(k," ".join(v)) for k,v in self.header_dict.items()])
        self.headers["content-security-policy"] = csp_string

    def add_source(self, key, value):
        if key not in self.header_dict.keys():
            self.header_dict[key] = [value]
        else:
            self.header_dict[key].append(value)
        self.rebuild_headers()