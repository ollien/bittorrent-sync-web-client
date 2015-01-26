BitTorrent Sync Web Client
==========================

A web client for Bit Torrent Sync.

I made this so I could finally use Btsync as opposed to Dropbox, since the major dealbreaker was that Btsync didn't have a web client.

I Run it with uwsgi and nginx, but it should work without them. 

This is my nginx config, which is pretty essential in order for this to work with nginx.

```
upstream btsyncWeb{
	server 127.0.0.1:8000;
}
server {
	listen 8080;
	server_name 0.0.0.0:8080;
	include uwsgi_params;
	client_max_body_size 128M;
	location / {
		auth_basic "Login pls";
		auth_basic_user_file /etc/nginx/.htpasswd;
		uwsgi_pass btsyncWeb;
	}
	location /download {
		internal;
		alias /mnt/bakery;
	}
	location /public {
		auth_basic "off";
		uwsgi_pass btsyncWeb;
	}
	location /static {
		alias /home/pi/btsync/BitTorrentSyncWeb/static;
	}
}
```
![Screenshot](https://raw.githubusercontent.com/ollien/BitTorrent-Sync-Web-Client/master/README_SCREENSHOT.png)
