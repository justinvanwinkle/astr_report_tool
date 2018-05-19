Alias /robots.txt /usr/local/wsgi/static/robots.txt
Alias /favicon.ico /usr/local/wsgi/static/favicon.ico

AliasMatch /([^/]*\.css) /usr/local/wsgi/static/styles/$1

Alias /media/ /usr/local/wsgi/static/media/

<Directory /usr/local/wsgi/static>
Order deny,allow
Allow from all
</Directory>

WSGIScriptAlias / /usr/local/wsgi/scripts/myapp.wsgi

<Directory /usr/local/wsgi/scripts>
Order allow,deny
Allow from all
</Directory>
