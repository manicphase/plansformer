# plansformer
proxy that transforms data sent to the pleroma frontend.

This isn't quite ready to be a reverse proxy yet, but does work as a local proxy pretty well.

## to play around with it

A config file needs creating in the root directory

```
[twitter]
BearerToken=TheTokenYouGetFromSigningUpForADeveloperAccountOnTwitter

[home]
homeurl=https://TheSiteYouWantToProxy.com
```

run `pip install -r requirements.txt` to install required packages

run `python injector.py` to run the server

go to `http://localhost:8182` to see the plansformed version of your pleroma instance
