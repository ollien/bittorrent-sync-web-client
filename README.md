BitTorrent Sync Web Client
==========================

A web client for BitTorrent Sync, using cherrypy and Project Polymer.

This was made so in order to switch from BitTorrent Sync from Dropbox, since the major dealbreaker was that BitTorrent Sync didn't have a web client.

It can be run using uwsgi and nginx, using the below config for nginx, but it can be run without them.


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
