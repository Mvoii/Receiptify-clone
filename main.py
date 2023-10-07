from flask import Flask, redirect, url_for, render_template, session, request

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os
import time
from time import gmtime, strftime

# defining CONSTS
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_key"
TOKEN_INFO = "token_info"
SECRET_KEY = "secret_key"

SHORT_TERM = "short_term"
MEDIUM_TERM = "medium_term"
LONG_TERM = "long_term"

def create_spotify_oauth():
    return SpotifyOAuth (
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external = True),
        scope = "user-top-read user-library-read"
    )

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SESSION_COOKIE_NAME"] = "my Cookie"


# login page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    sp_oath = SpotifyOAuth(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external = True),
        scope = "user-top-read user-library-read"
    )
    auth_url = sp_oath.get_authorize_url()
    return redirect(auth_url)

# redirect page
@app.route("/redirectPage")
def redirectPage():
    code = request.args.get("code") # redirectPage?code=TOKEN, returns TOKEN
    sp_oath = SpotifyOAuth (
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        redirect_uri = url_for("redirectPage", _external = True),
        scope = "user-top-read user-library-read"
    )
    session.clear()
    code = request.args.get("code")
    token_info = sp_oath.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for("receipt", _external = True))


# define get-token
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = (token_info["expires_at"] - now < 60)
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    return token_info

#receipt page
@app.route("/receipt")
def receipt():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    sp = spotipy.Spotify(
        auth = token_info["access_token"]
    )

    current_user_name = sp.current_user()['display_name']
    short_term = sp.current_user_top_tracks (
        limit = 10,
        offset = 0,
        time_range = SHORT_TERM
    )
    medium_term = sp.current_user_top_tracks (
        limit = 10,
        offset = 0,
        time_range = MEDIUM_TERM
    )
    long_term = sp.current_user_top_tracks (
        limit = 10,
        offset = 0,
        time_range = LONG_TERM
    )
    
    if os.path.exists(".cache"):
        os.remove(".cache")
    return render_template("receipt.html", user_display_name = current_user_name, short_term=short_term, medium_term=medium_term, long_term=long_term, currentTime=gmtime())
