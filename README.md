# plansformer
proxy that transforms data sent to the pleroma frontend.

This is is experimental software still in development. Useful so far on small instances, but probably not ready for big instances until some kind of custom config is sorted out.

## to play around with it

A `config.conf` file needs creating in the root directory

```
[twitter]
BearerToken = TheTokenYouGetFromSigningUpForADeveloperAccountOnTwitter

[home]
homeurl = https://TheSiteYouWantToProxy.com
```

## to install

run `pip install -r requirements.txt` to install required packages

run `python injector.py` to run the server

go to `http://localhost:8182` to see the plansformed version of your pleroma instance

## to run as reverse proxy

* remember to change the `homeurl` value to your internal address; probably "http://localhost:4000 *

assuming you've followed the standard installation instructions to install pleroma, you can make the following changes to your pleroma nginx config.

copy the default config: 
`cp /opt/pleroma/installation/pleroma.nginx /opt/pleroma/installation/pleroma.nginx.plansformer`

edit the new file: `nano /opt/pleroma/installation/pleroma.nginx.plansformer` with the following change near the bottom of the file

```
    location / {
        proxy_pass http://phoenix;
    }
```

to

```
    location / {
        proxy_pass_request_headers on;
        proxy_pass        http://localhost:8182;

        limit_except GET {
           proxy_pass http://phoenix;
        }
    }
```

create a systemd by running `nano /etc/systemd/system/plansformer.service` and populating the file with the following content

```
[Unit]
Description=plansformer service
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory=[ROOT FOLDER OF YOUR PLANSFORMER PROJECT]
ExecStart=python injector.py

[Install]
WantedBy=multi-user.target
```
run the server via the command `systemctl enable plansformer.service` 

### to switch the proxy on run the following lines

```
systemctl restart plansformer.service
cp /opt/pleroma/installation/pleroma.nginx.plansformer /etc/nginx/sites-available/pleroma.nginx
systemctl restart nginx
```

### to switch the proxy off run

```
cp /opt/pleroma/installation/pleroma.nginx /etc/nginx/sites-available/pleroma.nginx
systemctl restart nginx
```