import base64
import datetime
import hashlib
import secrets
import time
import urllib.parse
from uuid import uuid4

from requests import Session as Requests

from eve_etl.Common.Storage import session as db_ses
from eve_etl.Models import ConfigModel


class EVEAuth:
    def __init__(self, client_id: str, client_secret: str, redir_url: str = "http://localhost:5555/oauth/callback",
                 scope: list = None):
        self.client_id = client_id
        self._client_secret = client_secret
        self._redir_url = urllib.parse.quote(redir_url, safe="")
        self._scope = urllib.parse.quote(" ".join(scope), safe="") if scope is not None else ""

        self._webcli = Requests()
        self._webcli.headers.update({
            "Accept": "application/json",
            "User-Agent": "EVE-ETL by DACRepair <dacrepair@gmail.com>"
        })

        self._db_ses = db_ses()

    def gen_auth(self):
        url = "https://login.eveonline.com/v2/oauth/authorize/"

        state = str(uuid4())

        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32))
        chash = hashlib.sha256()
        chash.update(challenge)
        chash = base64.urlsafe_b64encode(chash.digest()).decode().replace("=", "")

        params = {
            "response_type": "code",
            "redirect_uri": self._redir_url,
            "client_id": self.client_id,
            "code_challenge": chash,
            "code_challenge_method": "S256",
            "state": state
        }
        params = ["{}={}".format(k, v) for k, v in params.items()]
        params = "&".join(params)

        return "{}?{}".format(url, params), state, challenge

    def gen_token(self, code: str, challenge: str):
        url = "https://login.eveonline.com/v2/oauth/token"
        params = {"grant_type": "authorization_code", "code": code}
        params.update({"code_verifier": challenge})
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
        retr = self._webcli.post(url, headers=headers, data=params, auth=(self.client_id, self._client_secret))
        if retr.status_code == 200:
            try:
                return retr.json()
            except:
                return None
        else:
            return None

    def _gen_refresh(self, refresh_token: str):
        url = "https://login.eveonline.com/v2/oauth/token"
        params = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com"}
        retr = self._webcli.post(url, data=params, headers=headers, auth=(self.client_id, self._client_secret))
        if retr.status_code == 200:
            return retr.json()
        else:
            return None

    def get_token(self):
        ttl = float(self.get_config("expires")) - time.mktime(datetime.datetime.utcnow().timetuple())
        if ttl <= 0:
            refresh_token = self.get_config("refresh_token")
            token = self._gen_refresh(refresh_token)
            utcnow = time.mktime(datetime.datetime.utcnow().timetuple())
            self.set_config(name="access_token", value=token['access_token']),
            self.set_config(name="expires", value=str(utcnow + token['expires_in'])),
            self.set_config(name="refresh", value=token['refresh_token'])
        return self.get_config("access_token")

    def get_config(self, name):
        name = "authserver_{}".format(name).lower()
        query = self._db_ses.query(ConfigModel).filter(ConfigModel.name == name)
        if query.count() == 1:
            return query.one().value
        else:
            return None

    def set_config(self, name, value):
        name = "authserver_{}".format(name).lower()
        query = self._db_ses.query(ConfigModel).filter(ConfigModel.name == name)
        if query.count() == 0:
            self._db_ses.add(ConfigModel(name=name, value=value))
            self._db_ses.commit()
        elif query.count() == 1:
            query.one().value = value
            self._db_ses.commit()
        else:
            query.delete()
            self._db_ses.add(ConfigModel(name=name, value=value))
            self._db_ses.commit()
        return

    def del_config(self, name):
        name = "authserver_{}".format(name).lower()
        query = self._db_ses.query(ConfigModel).filter(ConfigModel.name == name)
        retr = query.count()
        query.delete()
        self._db_ses.commit()
        return retr
