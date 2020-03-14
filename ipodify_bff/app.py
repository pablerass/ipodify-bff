# -*- coding: utf-8 -*-
"""ipodify BFF service to keep oauth session for ipodify UI."""
import os
import requests
import urllib

from flask import Flask, request, redirect, session
from flask_session import Session


SESSION_SECRET_KEY = os.getenv('SESSION_SECRET_KEY')
SPOTIFY_OAUTH_CLIENT_ID = os.getenv('SPOTIFY_OAUTH_CLIENT_ID')
SPOTIFY_OAUTH_CLIENT_SECRET = os.getenv('SPOTIFY_OAUTH_CLIENT_SECRET')
SPOTIFY_OAUTH_URL = os.getenv('SPOTIFY_OAUTH_URL', "https://accounts.spotify.com")
IPODIFY_API_URL = os.getenv('IPODIFY_API_URL')
IPODIFY_BFF_URL = os.getenv('IPODIFY_BFF_URL')

AUTHORIZE_PARAMS = {
    "response_type": "code",
    "client_id": SPOTIFY_OAUTH_CLIENT_ID,
    "redirect_uri": f"{IPODIFY_BFF_URL}/callback",
    "scope": " ".join([
        # "playlist-read-collaborative",
        # "playlist-read-private",
        # "user-follow-read",
        "user-library-read",
    ])
}
SPOTIFY_AUTHORIZE_URL = f"{SPOTIFY_OAUTH_URL}/authorize?{urllib.parse.urlencode(AUTHORIZE_PARAMS)}"
SPOTIFY_TOKEN_URL = f"{SPOTIFY_OAUTH_URL}/api/token"
# TODO: Get methods from external library
HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE',
                'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

app = Flask(__name__)
app.secret_key = SESSION_SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
s = Session()
s.init_app(app)


@app.route('/login')
def login():
    """Redirect to Spotify authorize page."""
    return redirect(SPOTIFY_AUTHORIZE_URL)


@app.route('/callback')
def callback():
    """Process Spotify oauth authorize callback."""
    data = {
        "grant_type": "authorization_code",
        "code": request.args.get("code"),
        "redirect_uri": f"{IPODIFY_BFF_URL}/callback"
    }
    r = requests.post(SPOTIFY_TOKEN_URL, data=data, auth=(SPOTIFY_OAUTH_CLIENT_ID, SPOTIFY_OAUTH_CLIENT_SECRET))
    r.raise_for_status()
    session['access_token'] = r.json()['access_token']
    session['token_type'] = r.json()['token_type']
    session['expires_in'] = r.json()['expires_in']
    session['refresh_token'] = r.json()['refresh_token']
    return ""


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def proxy(path):
    """Redirect requests to API server adding authentication headers."""
    # TODO: Implement token renewal and login redirection if not authenticated
    updated_headers = dict(request.headers)
    updated_headers.update({
        "Authorization": f"Bearer {session.get('access_token')}"
    })
    response = requests.request(method=request.method, url=f"{IPODIFY_API_URL}/{path}",
                                data=request.data, headers=updated_headers)
    return response.content, response.status_code
