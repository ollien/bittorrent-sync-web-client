BitTorrent Sync Web Client
==========================

A web client for BitTorrent Sync, using cherrypy and Project Polymer.

This can allow one to switch to BitTorrent Sync from Dropbox, since a major disadvantage to BitTorrentSync is that BitTorrent Sync doesn't have a web client.

It can be run using uwsgi and nginx, using the below nginx config (Make sure to replace {{path/to/storage}} and {{path/to/static}} with a path to where btsync is storing directories and a path to the static files directory respectivley.), but it can be run without them.


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
		auth_basic "Login please";
		auth_basic_user_file /etc/nginx/.htpasswd;
		uwsgi_pass btsyncWeb;
	}
	location /download {
		internal;
		alias {{/path/to/btsync/storage}};
	}
	location /public {
		auth_basic "off";
		uwsgi_pass btsyncWeb;
	}
	location /static {
		alias {{/path/to/static}};
	}
}
```
![Screenshot](https://raw.githubusercontent.com/ollien/BitTorrent-Sync-Web-Client/master/README_SCREENSHOT.png)
