import re


def fix_urls(text):
    pat_url = re.compile(  r'''
                    (?x)( # verbose identify URLs within text
        (http|ftp|gopher|https) # make sure we find a resource type
                    :// # ...needs to be followed by colon-slash-slash
            (\w+[:.]?){2,} # at least two domain groups, e.g. (gnosis.)(cx)
                    (/?| # could be just the domain name (maybe w/ slash)
                [^ \n\r"]+ # or stuff then space, newline, tab, quote
                    [\w/]) # resource name ends in alphanumeric or slash
        (?=[\s\.,>)'"\]]) # assert: followed by white or clause ending
                        ) # end of match group
                        ''')

    for url in re.findall(pat_url, text):
        text = text.replace(url[0], '<a href="%(url)s">%(url)s</a>' % {"url" : url[0]})

    return text