from waitress import serve
from shprote.wsgi import wsgi_app
import os


waitress_args = {}

if os.environ.get("DYNO"):  # Expose the socket to ngnix if running on Heroku
    waitress_args["unix_socket"] = "/tmp/nginx.socket"
    open("/tmp/app-initialized", "w").close()
else:
    waitress_args = {"port": os.environ.get("PORT", 8080)}

serve(wsgi_app, **waitress_args)
