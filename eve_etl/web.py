import datetime
import os
import time
from uuid import uuid4

from flask import Flask, session, request, redirect, render_template
from flask_bootstrap import Bootstrap
from requests import Session

from eve_etl import config, auth

flask = Flask(__name__, template_folder=os.path.normpath(os.getcwd() + "/templates"))
flask.config['SECRET_KEY'] = config.get("AuthServer", "secret_key", default=str(uuid4()))
Bootstrap(flask)


@flask.route("/")
def index():
    if auth.get_config("access_token") is None:
        url, state, challenge = auth.gen_auth()
        session['state'] = state
        session['challenge'] = challenge
        return render_template("index.html", data=dict(logged_in=False, url=url))
    else:
        char_data = dict(logged_in=True)
        char_data.update({
            "char_id": auth.get_config("char_id"),
            "char_name": auth.get_config("char_name"),
            "char_title": auth.get_config("char_title"),
            "alliance_name": auth.get_config("alliance_name"),
            "corporation_name": auth.get_config("corporation_name"),
            "faction_name": auth.get_config("faction_name")
        })
        return render_template("index.html", data=char_data)


@flask.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code", "")
    challenge = session.get("challenge", "")
    state = session.get("state", "THIS IS FAIL") == request.args.get("state", "")
    if state:
        token = auth.gen_token(code, challenge)
        utcnow = time.mktime(datetime.datetime.utcnow().timetuple())
        auth.set_config(name="access_token", value=token['access_token']),
        auth.set_config(name="expires", value=str(utcnow + token['expires_in'])),
        auth.set_config(name="refresh", value=token['refresh_token'])
        char_data = dict()
        token = auth.get_token()
        ses = Session()
        headers = {"Authorization": "Bearer {}".format(token), "X-User-Agent": auth.client_id}
        verify = ses.get("https://esi.evetech.net/verify/", headers=headers).json()
        char_data.update({"char_id": verify['CharacterID']})

        c = ses.get("https://esi.evetech.net/v4/characters/{}/".format(char_data['char_id']), headers=headers).json()
        char_data.update({"char_name": c.get('name'),
                          "char_title": c.get("title"),
                          "alliance_id": c.get('alliance_id'),
                          "corporation_id": c.get('corporation_id'),
                          "faction_id": c.get("faction_id")})

        if char_data.get("corporation_id") is not None:
            corp = ses.get(
                "https://esi.evetech.net/v4/corporations/{}/".format(char_data.get("corporation_id")),
                headers=headers).json()
            char_data.update({"corporation_name": corp.get("name")})

        if char_data.get("alliance_id") is not None:
            alli = ses.get("https://esi.evetech.net/v4/alliances/{}/".format(char_data.get("alliance_id")),
                           headers=headers).json()
            char_data.update({"alliance_name": alli.get("name")})

        if char_data.get("faction_id") is not None:
            fact = ses.get("https://esi.evetech.net/v2/universe/factions/", headers=headers).json()
            fact = [x['name'] for x in fact if x['faction_id'] == char_data.get("faction_id")]
            fact = fact[0] if len(fact) > 0 else None
            char_data.update({"faction_name": fact})

        for name, value in char_data.items():
            auth.set_config(name, str(value))

    return redirect("/")


@flask.route("/oauth/logout")
def logout():
    auth.purge_config()
    return redirect("/")
